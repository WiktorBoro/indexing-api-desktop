from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import httplib2
import tkinter as tk
import webbrowser


class IndexingApi:
    def __init__(self):
        self.feedback = ''
        self.command = "URL_UPDATED"
        self.root = tk.Tk()
        self.root.title("Indexing API v 1.1")
        self.interfejs_indexing_api()

    def change_sending_command(self, command):
        self.command = command
        if self.command == "URL_UPDATED":
            self.button_de_index.config(state='normal')
            self.button_index.config(state='disabled')

        elif self.command == "URL_DELETED":
            self.button_de_index.config(state='disabled')
            self.button_index.config(state='normal')

    def disabled_label(self):
        self.button_index.config(state='disabled')
        self.button_de_index.config(state='disabled')
        self.button.config(state='disabled')
        self.input_list_url.config(state='disabled')
        self.file_path.config(state='disabled')

    def enable_label(self):
        self.button_index.config(state='normal')
        self.button_de_index.config(state='normal')
        self.button.config(state='normal')
        self.input_list_url.config(state='normal')
        self.file_path.config(state='normal')

    def response_area_show(self):
        self.canvas1.itemconfig(tagOrId=self.canvas_response_label_feedback, state='normal')
        self.canvas1.itemconfig(tagOrId=self.canvas_response_x, state='normal')
        self.canvas1.itemconfig(tagOrId=self.canvas_response_y, state='normal')

    def response_area_hide(self):
        self.canvas1.itemconfig(tagOrId=self.canvas_response_label_feedback, state='hidden')
        self.canvas1.itemconfig(tagOrId=self.canvas_response_x, state='hidden')
        self.canvas1.itemconfig(tagOrId=self.canvas_response_y, state='hidden')

    def print_response(self):
        # print response
        self.response_area_show()

        self.label_feedback.insert("end", self.feedback)
        self.label_feedback.config(state='disabled', wrap='none')

        if "Invalid" in self.feedback:
            self.enable_label()

    def valid_del_url(self):
        # makes sure you know what you are doing
        self.disabled_label()

        self.response_area_hide()

        def options_are_selected(option):
            button_yes.destroy()
            button_no.destroy()
            are_you_sure.destroy()
            if option == "YES":
                self.send_to_index()
            elif option == "NO":
                self.enable_label()
        are_you_sure = tk.Label(self.root, text="All URL from list will be delete from Google index"
                                                " and lose position."
                                                " Are u sure?")

        button_yes = tk.Button(text='YES', command=lambda: options_are_selected("YES"))
        button_no = tk.Button(text='NO', command=lambda: options_are_selected("NO"))
        self.canvas1.create_window(350, 380, window=button_yes)
        self.canvas1.create_window(450, 380, window=button_no)
        self.canvas1.create_window(400, 350, window=are_you_sure)

    def send_to_index(self):
        path = self.file_path.get()
        list_url = self.input_list_url.get("1.0", "end")
        self.disabled_label()

        # checking if the cells are completed correctly
        if path and 0 < len(list_url.split('\n')) <= 200:

            # turns the list into a dictionary to send
            url_dict = dict.fromkeys(list(list_url.splitlines()), self.command)
            path = path.replace("\\", "\\\\")

            # send indexing requests
            self.indexing_api(url_dict=url_dict, path=path)

            # print response
            self.print_response()

        elif len(list_url.split('\n')) > 200:
            self.enable_label()
            max_links_text = tk.Label(self.root, text="Maximum 200 links per day per project")
            self.canvas1.create_window(400, 350, window=max_links_text)
        elif not path and list_url:
            self.enable_label()
            complete_fields_text = tk.Label(self.root, text="Complete the above fields")
            self.canvas1.create_window(400, 350, window=complete_fields_text)

    def interfejs_indexing_api(self):
            # frontend

            self.canvas1 = tk.Canvas(self.root, width=800, height=500)
            self.canvas1.pack()

            path_text = tk.Label(self.root, text="Insert the full path to the verification file")
            self.canvas1.create_window(400, 20, window=path_text)

            input_url_text = tk.Label(self.root, text="Insert links (1 link per line) (maximum 200 links per day per project)")
            self.canvas1.create_window(400, 110, window=input_url_text)

            text_guide = tk.Label(self.root, text="Link to the guide to obtaining the authorization file in Polish")
            self.canvas1.create_window(400, 495, window=text_guide)

            link = tk.Label(self.root, text="https://docs.google.com/document/d/1gRk3wv_7rN5ZUe4bW6q8_mODWiYhjeicQekEcZTJmlo/edit#",
                            fg="blue", cursor="hand2")
            link.pack()
            link.bind("<Button-1>", lambda event: webbrowser.open(link.cget("text")))

            self.file_path = tk.Entry(self.root)
            self.canvas1.create_window(400, 50, window=self.file_path, width=750)

            self.input_list_url = tk.Text(self.root)
            self.canvas1.create_window(400, 200, window=self.input_list_url, height=150, width=750)
            text_scroll_y = tk.Scrollbar(self.root, orient='vertical', command=self.input_list_url.yview)
            self.canvas1.create_window(785, 200, window=text_scroll_y, height=150)

            self.button_index = tk.Button(text='URL Index', command=lambda: self.change_sending_command('URL_UPDATED'))
            self.button_de_index = tk.Button(text='URL deleted', command=lambda: self.change_sending_command('URL_DELETED'))
            self.button = tk.Button(text='Index', command=lambda: self.send_to_index()
                                                                  if self.command != 'URL_DELETED'
                                                                  else self.valid_del_url())

            # response area
            self.label_feedback = tk.Text(self.root)
            text_scroll_x = tk.Scrollbar(self.root, orient='horizontal',
                                              command=self.label_feedback.xview)
            text_scroll_y = tk.Scrollbar(self.root, orient='vertical',
                                              command=self.label_feedback.yview)

            self.canvas_response_x = self.canvas1.create_window(400, 415, window=text_scroll_x,
                                                                width=750, state='hidden')
            self.canvas_response_y = self.canvas1.create_window(785, 350, window=text_scroll_y,
                                                                height=100, state='hidden')

            self.canvas_response_label_feedback = self.canvas1.create_window(400, 355,
                                                                            window=self.label_feedback,
                                                                            height=100, width=750, state='hidden')
            # end response area

            self.canvas1.create_window(400, 290, window=self.button)
            self.canvas1.create_window(350, 80, window=self.button_index)
            self.canvas1.create_window(450, 80, window=self.button_de_index)
            self.canvas1.pack()
            self.root.mainloop()

    def insert_feedback(self, *args):
        if args is not None:
            feedback = str(args[2]) + '\n'
        else:
            feedback = str(args) + '\n'
        self.feedback += feedback

    def indexing_api(self, url_dict, path):
        requests = url_dict

        json_key_file = path

        scopes = ["https://www.googleapis.com/auth/indexing"]
        # Authorize credentials
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scopes=scopes)
            credentials.authorize(httplib2.Http())
        except FileNotFoundError:
            self.feedback = "Invalid file or file path"
            return self.print_response()

        # Build service
        service = build('indexing', 'v3', credentials=credentials)

        batch = service.new_batch_http_request(callback=self.insert_feedback)

        for url, api_type in requests.items():
            batch.add(service.urlNotifications().publish(
                body={"url": url, "type": api_type}))

        batch.execute()


if __name__ == "__main__":
    IndexingApi()
