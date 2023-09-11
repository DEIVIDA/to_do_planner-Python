from back import Entries, Task
import PySimpleGUI as sg
from datetime import datetime


# padaryt tvarkinga lentele -- Ilya
# pagerint grafine vartotojo sasaja -- Deivida

sg.theme("LightGrey1")

green_team = Entries()

main_layout = [
    [sg.Text("Type task name", font=("Helvetica", 16))],
    [
        sg.InputText(key="-TASK-", font=("Helvetica", 14)),
        sg.Button("Add Task", font=("Helvetica", 14)),
    ],
    [sg.Listbox(values=[], size=(30, 5), key="-TASK-LIST-", font=("Helvetica", 14))],
    [
        sg.Button("Delete Task", font=("Helvetica", 14)),
        sg.Button("Escape", font=("Helvetica", 14)),
        sg.Button("Show as a table", font=("Helvetica", 14)),
    ],
    [
        sg.Button("Save", font=("Helvetica", 14)),
        sg.Button("Load", font=("Helvetica", 14)),
    ],
]

window = sg.Window("To-Do List", main_layout)

task_add_layout = [
    [
        sg.Text("task description", font=("Helvetica", 12)),
        sg.InputText(key="-DESCRIPTION-"),
    ],
    [
        sg.Text("Task deadline (MM/DD, HH:MM)", font=("Helvetica", 12)),
        sg.InputText(key="-DEADLINE-"),
    ],
    [sg.Button("Submit info", font=("Helvetica", 14))],
]


task_add_window = sg.Window("Additional layout", task_add_layout, finalize=True)
task_add_window.hide()

while True:
    main_event, main_values = window.read()

    if main_event == sg.WINDOW_CLOSED or main_event == "Escape":
        green_team.save_to_pickle("autosave_todo.pkl")
        break

    elif main_event == "Add Task" and main_values["-TASK-"]:
        window.hide()
        task_add_window.un_hide()
        task_add_event, task_add_values = task_add_window.read()

        if task_add_event == "Submit info":
            task = Task(
                main_values["-TASK-"],
                task_add_values["-DESCRIPTION-"],
                task_add_values["-DEADLINE-"],
            )
            green_team.add_task(task)
            task_add_window["-DESCRIPTION-"].update(value="")
            task_add_window["-DEADLINE-"].update(value="")
        task_add_window.hide()
        window.un_hide()

        window["-TASK-LIST-"].update(values=green_team.task_list)
        window["-TASK-"].update(value="")

    elif main_event == "Delete Task":
        selected_tasks = main_values["-TASK-LIST-"]

        if selected_tasks:
            selected_task = selected_tasks[0]
            green_team.task_list.remove(selected_task)
            window["-TASK-LIST-"].update(values=green_team.task_list)

    elif main_event == "Save":
        green_team.save_to_pickle("todo.pkl")

    elif main_event == "Load":
        green_team.load_from_pickle("todo.pkl")
        window["-TASK-LIST-"].update(values=green_team.task_list)

    elif main_event == "Show as a table":
        table_values = []
        for task in green_team.task_list:
            if isinstance(task.deadline, str):
                try:
                    task.deadline = datetime.strptime(f"2023/{task.deadline}", "%Y/%m/%d, %H:%M")
                except ValueError:
                    try:
                        task.deadline = datetime.strptime(task.deadline, "%Y/%m/%d %H:%M")
                    except ValueError:
                        task.deadline = datetime.strptime(task.deadline, "%Y-%m-%d %H:%M:%S")

            time_left = task.deadline - datetime.now().replace(microsecond=0)
            if datetime.now() > task.deadline:
                task.status = "Late"
                table_values.append([task.name, task.description, str(time_left), task.status])
            else:
                table_values.append([task.name, task.description, str(time_left), task.status])

        table_layout = [
            [
                sg.Table(
                    values=table_values,
                    headings=[
                        "Task name",
                        "Description",
                        "Time left to Deadline",
                        "Status",
                    ],
                    auto_size_columns=True,
                    num_rows=10,
                    key="-TABLE-",
                    text_color="black",
                    justification="center",
                    enable_events=True,
                    row_colors=[(i,'white') for i in range(10)],
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE
                )
            ],
            [sg.Button("Back", font=("Helvetica", 14)), sg.Button('Change status', font=("Helvetica", 14), key='-STATUS-') ]
        ]

        table_window = sg.Window("Tasks table", table_layout)
        status_choices = ['in progress', 'done', 'Late']
        def custom_status_element(key, status):
            return sg.Combo(values=status_choices, default_value=status, key=key, background_color='white')

        while True:
            table_event, table_values = table_window.read()

            if table_event == 'Back' or table_event == sg.WIN_CLOSED:
                break
            elif table_event == '-STATUS-':
                if table_values['-TABLE-']:
                    selected_row_index = table_values['-TABLE-'][0]

                    status_element = custom_status_element('-STATUS-', table_values['-TABLE-'][selected_row_index])

                    status_layout = [
                        [sg.Text('Select Status:', pad=(0, (0, 10)))],
                        [status_element],
                        [sg.Button('OK'), sg.Button('Cancel')]
                    ]

                    status_window = sg.Window('Select Status', status_layout, finalize=True, keep_on_top=True)

                    while True:
                        status_event, status_values = status_window.read()

                        if status_event == sg.WIN_CLOSED or status_event == 'Cancel':
                            break

                        elif status_event == 'OK':
                            new_status = status_values['-STATUS-']
                            print(new_status)
                            green_team.task_list[selected_row_index].status = new_status
                            table_values = []
                            for task in green_team.task_list:
                                table_values.append([task.name, task.description, task.deadline, task.status])
                            table_window['-TABLE-'].update(values=table_values)
                            status_window.close()
                            break

        table_window.close()
        window.un_hide()

window.close()
