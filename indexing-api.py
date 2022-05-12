from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import httplib2
import tkinter as tk
import webbrowser


class IndexingApi:
    def __init__(self):
        self.feedback = ''
        self.command = "URL_UPDATED"

    def change_sending_command(self, command):
        self.command = command
        if command == "URL_UPDATED":
            self.button_de_index.config(state='normal')
            self.button_index.config(state='disabled')

        elif command == "URL_DELETED":
            self.button_de_index.config(state='disabled')
            self.button_index.config(state='normal')

    def interfejs_indexing_api(self):

        def disabled_label():
            self.button_index.config(state='disabled')
            self.button_de_index.config(state='disabled')
            button.config(state='disabled')
            input_list_url.config(state='disabled')
            file_path.config(state='disabled')

        def enable_label():
            self.button_index.config(state='normal')
            self.button_de_index.config(state='normal')
            button.config(state='normal')
            input_list_url.config(state='normal')
            file_path.config(state='normal')

        def valid_del_url():
            # makes sure you know what you are doing
            disabled_label()

            def options_are_selected(option):
                button_yes.destroy()
                button_no.destroy()
                are_you_sure.destroy()
                if option == "YES":
                    send_to_index(sending_command=self.command)
                elif option == "NO":
                    enable_label()
            are_you_sure = tk.Label(root, text="All URL from list will be delete from Google index"
                                                " and lose position."
                                                " Are u sure?")

            button_yes = tk.Button(text='YES', command=lambda: options_are_selected("YES"))
            button_no = tk.Button(text='NO', command=lambda: options_are_selected("NO"))
            canvas1.create_window(350, 380, window=button_yes)
            canvas1.create_window(450, 380, window=button_no)
            canvas1.create_window(400, 350, window=are_you_sure)

        def send_to_index(sending_command):
            path = file_path.get()
            list_url = input_list_url.get("1.0","end")
            disabled_label()

            # checking if the cells are completed correctly
            if path and 0 < len(list_url.split('\n')) <= 200:
                # turns the list into a dictionary to send
                url_dict = dict.fromkeys(list(list_url.splitlines()), sending_command)
                path = path.replace("\\","\\\\")

                # send indexing requests
                response_feedback = IndexingApi().indexing_api(url_dict=url_dict, path=path)

                # print response
                label_feedback = tk.Text(root)
                label_feedback.insert("end", response_feedback)

                text_scroll_x = tk.Scrollbar(root, orient='horizontal', command=label_feedback.xview)
                text_scroll_y = tk.Scrollbar(root, orient='vertical', command=label_feedback.yview)
                canvas1.create_window(400, 415, window=text_scroll_x, width=750)
                canvas1.create_window(785, 350, window=text_scroll_y, height=100)

                label_feedback.config(state='disabled', wrap='none')
                canvas1.create_window(400, 355, window=label_feedback, height=100, width=750)

                if "Invalid" in response_feedback:
                    enable_label()

            elif len(list_url.split('\n')) > 200:
                enable_label()
                max_links_text = tk.Label(root, text="Maximum 200 links per day per project")
                canvas1.create_window(400, 350, window=max_links_text)
            elif not path and list_url:
                enable_label()
                complete_fields_text = tk.Label(root, text="Complete the above fields")
                canvas1.create_window(400, 350, window=complete_fields_text)

        # frontend
        root = tk.Tk()
        root.title("Indexing API v 1.1")

        canvas1 = tk.Canvas(root, width=800, height=500)
        canvas1.pack()

        path_text = tk.Label(root, text="Insert the full path to the verification file")
        canvas1.create_window(400, 20, window=path_text)

        input_url_text = tk.Label(root, text="Insert links (1 link per line) (maximum 200 links per day per project)")
        canvas1.create_window(400, 110, window=input_url_text)

        text_guide = tk.Label(root, text="Link to the guide to obtaining the authorization file in Polish")
        canvas1.create_window(400, 495, window=text_guide)

        link = tk.Label(root, text="https://docs.google.com/document/d/1gRk3wv_7rN5ZUe4bW6q8_mODWiYhjeicQekEcZTJmlo/edit#",
                        fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda event: webbrowser.open(link.cget("text")))

        file_path = tk.Entry(root)
        canvas1.create_window(400, 50, window=file_path, width=750)

        input_list_url = tk.Text(root)
        canvas1.create_window(400, 200, window=input_list_url, height=150, width=750)
        text_scroll_y = tk.Scrollbar(root, orient='vertical', command=input_list_url.yview)
        canvas1.create_window(785, 200, window=text_scroll_y, height=150)

        self.button_index = tk.Button(text='URL Index', command=lambda: self.change_sending_command('URL_UPDATED'))
        self.button_de_index = tk.Button(text='URL deleted', command=lambda: self.change_sending_command('URL_DELETED'))
        button = tk.Button(text='Index', command=lambda: send_to_index(sending_command=self.command)
                                                                       if self.command != 'URL_DELETED'
                                                                       else valid_del_url())

        canvas1.create_window(400, 290, window=button)
        canvas1.create_window(350, 80, window=self.button_index)
        canvas1.create_window(450, 80, window=self.button_de_index)
        canvas1.pack()
        root.mainloop()

    def insert_event(self, response, exception):
        if exception is not None:
            feedback = str(exception) + '\n'
        else:
            feedback = str(response) + '\n'
        self.feedback += feedback

    def indexing_api(self, url_dict,path):
        requests = url_dict

        JSON_KEY_FILE = path

        SCOPES = ["https://www.googleapis.com/auth/indexing"]
        # Authorize credentials
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
            credentials.authorize(httplib2.Http())
        except:
            return "Invalid file or file path"

        # Build service
        service = build('indexing', 'v3', credentials=credentials)

        batch = service.new_batch_http_request(callback=self.insert_event)

        for url, api_type in requests.items():
            batch.add(service.urlNotifications().publish(
                body={"url": url, "type": api_type}))

        batch.execute()
        return self.feedback


if __name__ == "__main__":
    IndexingApi().interfejs_indexing_api()
