from django.core.management.base import BaseCommand, CommandError
from tasks.tasks import TaskRunner, GradingStepsRunner
import pprint
from tasks import rpc

class Command(BaseCommand):
    help = 'Run test task from file'
    args = '<docker-name> <submission> <filename>'

    def exec_task(self, docker_image, submission, inputs, outputs):
        state = "/mnt/input"
        grade = 0


        with TaskRunner(docker_image, submission) as runner:

            for input_code, output_code in zip(inputs, outputs):
                input_result = rpc.prepare_input_command(input_code, state)
                print("Input")
                pprint.pprint(input_result)

                execution_result = runner.exec_step(input_result["command"])

                print("Execution result:")
                pprint.pprint(execution_result)
                try:
                    print("-----DOCKER STDOUT(DECODED)------")
                    print(execution_result.decode("utf8"))
                    print("-----------")
                except UnicodeError:
                    print("error decoding")

                output_result = rpc.parse_output_local(output_code, input_result["state"], execution_result, "", 0)
                state = output_result["state"]
                grade = grade + output_result["grade"]
                message = output_result["output_msg"]
                exec_next_step = output_result["exec_next_step"]

                print("Output")
                pprint.pprint(output_result)

                print("\n-----------\n")

                if not exec_next_step:
                    print("STOPPING")
                    break
        print("End grade {}\n".format(grade))

    def handle(self, *args, **options):
        inputs = []
        outputs = []

        with open(args[2], 'r') as infile:
            currentBuffer = ""


            for line in infile:
                if line.strip() == "#-----INPUT-TASK-STEP-----":
                    if currentBuffer != "":
                        outputs.append(currentBuffer)
                    currentBuffer = ""
                elif line.strip() == "#-----OUTPUT-TASK-STEP-----":
                    if currentBuffer != "":
                        inputs.append(currentBuffer)
                    currentBuffer = ""
                else:
                    currentBuffer += line

            if currentBuffer != "":
                outputs.append(currentBuffer)

        self.exec_task(args[0], args[1], inputs, outputs)
