import os.path
import pprint

from django.core.management.base import BaseCommand

from grader.base.task import Task


class Command(BaseCommand):
    help = 'Run test task from dir'
    args = '<task_definition_dir>'

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

                output_result = rpc.parse_output_local(
                    output_code, input_result["state"],
                    execution_result, "", 0)
                state = output_result["state"]
                grade = grade + output_result["grade"]
                exec_next_step = output_result["exec_next_step"]

                print("Output")
                pprint.pprint(output_result)

                print("\n-----------\n")

                if not exec_next_step:
                    print("STOPPING")
                    break
        print("End grade {}\n".format(grade))


    def add_arguments(self, parser):
        parser.add_argument('task_definition_dir', type=str)
        parser.add_argument('test_file_path', type=str)


    def handle(self, task_definition_dir, test_file_path, *args, **options):
        task = Task.from_dir(task_definition_dir)

        step_results = task.grade(test_file_path)

        output_format = ('Step: {1!s}\n'
                         'Marks: {2:d}/{3:d}\n'
                         '{4!s}\n'
                         '{0:-<40}\n'
                         'stdplex:\n{5!s}\n'
                         '{0:-<79}')

        total_marks = 0

        for step_name, step_result in step_results:
            total_marks += step_result['marks']

            if step_result['fail'] is True:
                style_func = self.style.ERROR
            elif step_result['marks'] == step_result['max_marks']:
                style_func = self.style.SUCCESS
            else:
                style_func = self.style.WARNING

            stdplex = step_result.get('testing_result', {}).get('stdplex', '')

            self.stderr.write(style_func(output_format.format(
                '',
                step_name,
                step_result['marks'], step_result['max_marks'],
                step_result['output_msg'], stdplex)))

        if total_marks == 0:
            style_func = self.style.ERROR
        elif total_marks >= task.max_marks:
            style_func = self.style.SUCCESS
        else:
            style_func = self.style.WARNING

        self.stderr.write(style_func('Total marks: {0:d}/{1:d}').format(
            total_marks, task.max_marks))

