from tkinter import *
from tkinter import ttk
import psycopg2
import json


from Shared import util
from Shared import data_access


class App(Tk):
    def __init__(self):
        super(App, self).__init__()

        self.title("Card Approval Control")
        self.minsize(600, 400)
        self.wm_iconbitmap("..\\Resources\\check.ico")

        self.clients = [10710]
        self.environments = ['dev']

        self.variable_version = "1.1.0"

        self.client_loads_list = \
            [
                {
                    "card_approval_control_id": 1,
                    "environment_tag": "dev",
                    "global_client_id": 10710,
                    "global_load_id": "2020Q1",
                    "global_load_version": "2020-06-04-21",
                    "isaac_client_num": 1071,
                    "approved_flag": 0,
                    "approved_by": "unknown"
                }
            ]

        self.dal = data_access.DataAccess(self.client_loads_list, self.clients, self.environments, "")

        self.host = StringVar(self)
        self.port = StringVar(self)
        self.db = StringVar(self)
        self.user_name = StringVar(self)
        self.pw = StringVar(self)
        self.environment = StringVar(self)
        self.client = IntVar(self)
        self.client2 = IntVar(self)
        self.load_id = StringVar(self)
        self.load_version = StringVar(self)
        self.approval_control_id = StringVar(self)
        self.approved_flag = IntVar()
        self.card_approval_output = StringVar()
        self.all_clients_flag = IntVar()

        self.client.trace('w', self.update_options_load_ids)
        self.load_id.trace('w', self.update_options_load_versions)

        tabControl = ttk.Notebook(self)
        self.tab1 = ttk.Frame(tabControl)
        tabControl.add(self.tab1, text="Account Credentials")

        self.tab2 = ttk.Frame(tabControl)
        tabControl.add(self.tab2, text="Approval Configuration Lookup")
        tabControl.pack(expand=1, fill="both")

        self.tab3 = ttk.Frame(tabControl)
        tabControl.add(self.tab3, text="Approval Control Refresh")
        tabControl.pack(expand=1, fill="both")

        self.path_to_json = "..\\Resources\connection.json"

        self.widgets_tab1()

        # default some connection params
        profile = util.load_connection_defaults(self.path_to_json)
        self.host = profile["host"]
        self.port = profile["port"]
        self.db = profile["db"]
        self.user_name = profile["user"]

        self.text_host.insert(0, self.host)
        self.text_port.insert(0, self.port)
        self.text_db.insert(0, self.db)
        self.text_user_name.insert(0, self.user_name)


    def widgets_tab1(self):
        label_frame_1 = LabelFrame(self.tab1, text="Connection Settings")
        label_frame_1.grid(column=0, row=0, padx=8, pady=4)

        label_host = Label(label_frame_1, text="Host:")
        label_host.grid(column=0, row=0, sticky='W')
        self.text_host = Entry(label_frame_1, textvariable=self.host, width=75)
        self.text_host.grid(column=1, row=0)
        label_port = Label(label_frame_1, text="Port:")
        label_port.grid(column=2, row=0, sticky='W')
        self.text_port = Entry(label_frame_1, textvariable=self.port, width=6)
        self.text_port.grid(column=3, row=0, sticky='W')

        label_db = Label(label_frame_1, text="Database Name:")
        label_db.grid(column=0, row=1, sticky='W')
        self.text_db = Entry(label_frame_1, textvariable=self.db, width=6)
        self.text_db.grid(column=1, row=1, sticky='W')

        label_user_name = Label(label_frame_1, text="UserName:")
        label_user_name.grid(column=0, row=2, sticky='W')
        self.text_user_name = Entry(label_frame_1, textvariable=self.user_name, width=40)
        self.text_user_name.grid(column=1, row=2, sticky='W')

        label_pw = Label(label_frame_1, text="Enter Your Password:")
        label_pw.grid(column=0, row=3, sticky='W')
        self.text_pw = Entry(label_frame_1, width=40, show='*')
        self.text_pw.grid(column=1, row=3, sticky='W')

        # add button "Connect and load client options"
        connect_refresh_btn = Button(label_frame_1, text="Connect and load client options", command=self.connect_db)
        connect_refresh_btn.grid(column=4, row=4, sticky=W)

        self.message_label1 = Label(label_frame_1, text="Ready.")
        self.message_label1.grid(column=0, row=5, sticky='W', columnspan=4)

        version_label = Label(label_frame_1, text="Version: " + self.variable_version)
        version_label.grid(column=4, row=6, sticky='E')

    def widgets_tab2(self):
        label_frame_2 = LabelFrame(self.tab2, text="Client Card Settings")
        label_frame_2.grid(column=0, row=0, padx=8, pady=4, sticky=W)

        label_env = Label(label_frame_2, text="Environment:")
        label_env.grid(column=0, row=0, sticky='W')
        optionmenu_env = OptionMenu(label_frame_2, self.environment, *self.environments)
        optionmenu_env.grid(column=1, row=0)
        label_global_client = Label(label_frame_2, text="Global Client ID:")
        label_global_client.grid(column=2, row=0, sticky='W')
        optionmenu_client = OptionMenu(label_frame_2, self.client, *self.clients)
        optionmenu_client.grid(column=3, row=0)

        label_load_id = Label(label_frame_2, text="Global Load ID:")
        label_load_id.grid(column=0, row=1, sticky='W')
        self.optionmenu_load_id = OptionMenu(label_frame_2, self.load_id, '')
        self.optionmenu_load_id.grid(column=1, row=1)
        label_global_load_version = Label(label_frame_2, text="Global Load Version:")
        label_global_load_version.grid(column=2, row=1, sticky='W')
        self.optionmenu_load_version = OptionMenu(label_frame_2, self.load_version, '')
        self.optionmenu_load_version.grid(column=3, row=1)
        search_refresh_btn = Button(label_frame_2, text="Refresh Card Approval results", command=self.load_result)
        search_refresh_btn.grid(column=4, row=1, sticky=W)

        self.label_frame_3 = LabelFrame(self.tab2, text="Approval Card Control Result")
        self.label_frame_3.grid(column=0, row=5, padx=8, pady=4)
        label_header = Label(self.label_frame_3, text="Approval Control ID        Environment Tag  | Client Client ID | Global Load ID | Global Load Version | Isaac Client Number |                  Approved By                          Approved Flag")
        label_header.grid(column=0, row=1, columnspan=3, sticky=W)

        self.approval_key_entry = Entry(self.label_frame_3, textvariable=self.approval_control_id, width=20)
        self.approval_key_entry.grid(column=0, row=2, sticky=W)
        self.text_approval_output = Entry(self.label_frame_3, textvariable=self.card_approval_output, width=115)
        self.text_approval_output.grid(column=1, row=2, sticky=W)
        self.approve_flg_chk_btn = Checkbutton(self.label_frame_3, text='', command=self.flag_changed, variable=self.approved_flag, onvalue=1, offvalue=0)
        self.approve_flg_chk_btn.grid(column=2, row=2, sticky=W)
        self.message_label2 = Label(self.label_frame_3, text="Ready.")
        self.message_label2.grid(column=0, row=3, sticky='W', columnspan=2)

    def widgets_tab3(self):
        label_frame_4 = LabelFrame(self.tab3, text="Load Latest Refresh Rows")
        label_frame_4.grid(column=0, row=0, padx=8, pady=4, sticky=W)
        label_global_client2 = Label(label_frame_4, text="Global Client ID:")
        label_global_client2.grid(column=0, row=0, sticky='W')
        optionmenu_client = OptionMenu(label_frame_4, self.client2, *self.clients)
        optionmenu_client.grid(column=1, row=0)
        all_clients_chk_btn = Checkbutton(label_frame_4, text='Load All Clients', variable=self.all_clients_flag, onvalue=1, offvalue=0)
        all_clients_chk_btn.grid(column=2, row=0, sticky=W)
        search_refresh_btn = Button(label_frame_4, text="Execute Insert", command=self.load_latest_refresh_click)
        search_refresh_btn.grid(column=4, row=1, sticky=W)
        self.message_label3 = Label(label_frame_4, text="Ready.")
        self.message_label3.grid(column=0, row=2, sticky='W', columnspan=4)

    def update_options_load_ids(self, *args):
        load_ids = self.dal.get_client_load_id_list(self.client.get())
        self.load_id.set(load_ids[0])
        menu = self.optionmenu_load_id['menu']
        menu.delete(0, 'end')
        for load_id in load_ids:
            menu.add_command(label=load_id, command=lambda global_load_id=load_id: self.load_id.set(global_load_id))

    def update_options_load_versions(self, *args):
        load_versions = self.dal.get_client_load_version_list(self.client.get(), self.load_id.get())
        self.load_version.set(load_versions[0])
        menu = self.optionmenu_load_version['menu']
        menu.delete(0, 'end')
        for load_version in load_versions:
            menu.add_command(label=load_version, command=lambda global_load_version=load_version: self.load_version.set(global_load_version))

    def load_latest_refresh_click(self, *args):
        if (len(self.text_host.get()) > 0 and len(self.text_port.get()) > 0 and len(self.text_db.get()) > 0
                and len(self.text_user_name.get()) > 0 and len(self.text_pw.get()) > 0):
            try:
                con = psycopg2.connect(
                    "dbname=" + self.text_db.get() + " host=" + self.text_host.get() + " port=" + self.text_port.get() \
                    + " user=" + self.text_user_name.get() + " password=" + self.text_pw.get())

                if self.dal.append_rows(con, self.all_clients_flag.get(), self.client2.get()) == 0:
                    self.message_label3.config(text=self.dal.get_message())
                else:
                    self.message_label2.config(text="Something went wrong or connection failed.")
            except Exception as error:
                self.message_label2.config(text="Connection to database failed: " + str(error))
        else:
            self.message_label2.config(text="Connection variables not set.")

    def load_result(self, *args):
        if self.dal.select_result(self.environment.get(), self.client.get(), self.load_id.get(), self.load_version.get()) == 0:
            aprv_flag = self.dal.get_approved_flag()

            if aprv_flag == 1:
                self.approved_flag.set(1)
            elif aprv_flag == 0:
                self.approved_flag.set(0)

            self.approval_key_entry.delete(0, 'end')
            self.approval_key_entry.insert(0, str(self.dal.get_approval_control_id()))
            self.text_approval_output.delete(0, 'end')
            self.text_approval_output.insert(0, self.dal.get_message())
        else:
            self.message_label2.config(text="Something went wrong: " + self.dal.get_message())

    def flag_changed(self, *args):
        if self.approved_flag.get() == 1:
            aprv_value = "1"
        else:
            aprv_value = "0"

        if (len(self.text_host.get()) > 0 and len(self.text_port.get()) > 0 and len(self.text_db.get()) > 0
                and len(self.text_user_name.get()) > 0 and len(self.text_pw.get()) > 0):
            try:
                con = psycopg2.connect(
                    "dbname=" + self.text_db.get() + " host=" + self.text_host.get() + " port=" + self.text_port.get() \
                    + " user=" + self.text_user_name.get() + " password=" + self.text_pw.get())
                if self.dal.approve_client_load(con, aprv_value, self.text_user_name.get(), self.approval_key_entry.get(), self.client.get(), self.environment.get()) == 0:
                    self.message_label2.config(text=self.dal.get_message())
                    self.load_result()
                else:
                    self.message_label2.config(text="Something went wrong or connection failed.")
            except Exception as error:
                self.message_label2.config(text="Connection to database failed: " + str(error))
        else:
            self.message_label2.config(text="Connection variables not set.")

    def connect_db(self):
        if (len(self.text_host.get()) > 0 and len(self.text_port.get()) > 0 and len(self.text_db.get()) > 0
                and len(self.text_user_name.get()) > 0 and len(self.text_pw.get()) > 0):
            try:
                con = psycopg2.connect(
                    "dbname=" + self.text_db.get() + " host=" + self.text_host.get() + " port=" + self.text_port.get()\
                    + " user=" + self.text_user_name.get() + " password=" + self.text_pw.get())

                if self.dal.set_client_load_list(con) == 0:
                    self.client_loads_list = self.dal.get_client_loads_list()
                    self.environments = self.dal.get_environments()
                    self.clients = self.dal.get_clients()
                    self.widgets_tab2()
                    self.widgets_tab3()
                    util.save_connection_defaults(self.text_user_name.get()[0:50], self.text_host.get()[0:150], self.text_port.get()[0:4], self.text_db.get()[0:5], self.path_to_json)
                    self.message_label1.config(text="Connected to db: [" + self.text_db.get() + "].")
                else:
                    self.message_label1.config(text=self.dal.get_message())
            except Exception as error:
                self.message_label1.config(text="Connection to database failed: " + str(error))
        else:
            self.message_label1.config(text="Connection variables not set.")

# Main: Load form
app = App()
app.mainloop()
