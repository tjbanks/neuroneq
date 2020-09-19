# -*- coding: utf-8 -*-
"""
Created on Tues Sept 18 20:11:54 CST 2020
@author: Tyler Banks
"""

import os
import threading
import matplotlib
import numpy as np

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

try:
    import Tkinter as tk # this is for python2
    import ttk
    import tkMessageBox as messagebox
except:
    import tkinter as tk # this is for python3
    from tkinter import ttk
    from tkinter import messagebox

matplotlib.use("TkAgg")


class Autoresized_Notebook(ttk.Notebook):
    def __init__(self, master=None, **kw):
        ttk.Notebook.__init__(self, master, **kw)
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self,event):
        event.widget.update_idletasks()
        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())

class CreateToolTip(object):
        """
        create a tooltip for a given widget
        https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
        """
        def __init__(self, widget, text='widget info'):
            self.waittime = 500     #miliseconds
            self.wraplength = 180   #pixels
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)
            self.id = None
            self.tw = None

        def enter(self, event=None):
            self.schedule()

        def leave(self, event=None):
            self.unschedule()
            self.hidetip()

        def schedule(self):
            self.unschedule()
            self.id = self.widget.after(self.waittime, self.showtip)

        def unschedule(self):
            id = self.id
            self.id = None
            if id:
                self.widget.after_cancel(id)

        def showtip(self, event=None):
            x = y = 0
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            # creates a toplevel window
            self.tw = tk.Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(self.tw, text=self.text, justify='left',
                        background="#ffffff", relief='solid', borderwidth=1,
                        wraplength = self.wraplength)
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tw
            self.tw= None
            if tw:
                tw.destroy()

class NeuronEQWindow():

    def __init__(self):
        self.root = tk.Tk()
        self.default_status = "Status: Ready"

        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.root.title("NeuronEQ (University of Missouri - Neural Engineering Lab) ")
        self.root.geometry('900x800')

        #self.root.resizable(0,0)
        self.root.config(menu=self.menu_bar())

        self.app_status = tk.StringVar(self.root,'')
        self.reset_app_status()

    def display(self):
        self.main()

    def menu_bar(self):
        def hello():
            print("hello!")
            
        def about():
            messagebox.showinfo("About", "Written for:\nProfessor Satish Nair's Neural Engineering Laboratory\nat The University of Missouri\n\nWritten by: Tyler Banks\n\nEmail tbg28@mail.missouri.edu with questions", icon='info')

        menubar = tk.Menu(self.root)
        
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        #filemenu.add_command(label="Open", command=hello)
        #filemenu.add_command(label="Save", command=hello)
        #filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        return menubar

    #pass the method that will create the content for your frame
    def bind_page(self,page, gen_frame):
        #### Scrollable Frame Window ####
        #https://stackoverflow.com/questions/42237310/tkinter-canvas-scrollbar
        frame = tk.Frame(page, bd=2)
        frame.pack(side="left",fill="both",expand=True)
        
        yscrollbar = tk.Scrollbar(frame)
        yscrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        xscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM,fill=tk.X)
        
        canvas = tk.Canvas(frame, bd=0,
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set,)
        
        xscrollbar.config(command=canvas.xview)
        yscrollbar.config(command=canvas.yview)
        
        f=tk.Frame(canvas)
        canvas.pack(side="left",fill="both",expand=True)
        canvas.create_window(0,0,window=f,anchor='nw')
        ###############################
        gen_frame(f)
        frame.update()
        canvas.config(scrollregion=canvas.bbox("all"))


    def parameters_page(self,root):
        '''
        Reads the parameters hoc file
        Lines should be formatted like:
        default_var("Variable","value")		// Comment to be tip
        '''
        param_has_changed = False
        params_file = os.path.join('setupfiles','parameters.hoc')
        
        top_option_frame = tk.LabelFrame(root, text="Plots")
        table_frame = tk.Frame(root)
        import_export_frame = tk.LabelFrame(root, text="Import/Export")
        
        top_option_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)
        table_frame.grid(column=0,row=1,sticky='news',padx=10,pady=5)
        import_export_frame.grid(column=1,row=0,sticky='news',padx=10,pady=5)

        general_frame = tk.LabelFrame(table_frame, text="Alpha/Beta Equations",fg="red",width=200)
        general_frame.grid(column=0,row=0,sticky='news',padx=10,pady=5)

        output_frame = tk.LabelFrame(table_frame, text="Output",fg="red")
        output_frame.grid(column=1,row=0,sticky='news',padx=10,pady=5)

        row_header = ['variable','value','comment','value_is_string']
        rows=[]
        
        def plot():
            self.alphaplot.clear()

            # 100 linearly spaced numbers
            x = np.linspace(-5,5,1000)

            # the function, which is y = x^2 here
            #y = x**2
            alpha_expression = self.alpha_row.value()
            alpha_expression = alpha_expression.replace("exp(","np.exp(")

            print(alpha_expression)

            y = x**2

            self.alphaline = self.alphaplot.plot(x,y)
                
            self.alphacanvas.draw()

            

        def verify1():
            print("Running Stimulation Evoked Contractions, case 1")

        def verify2():
            print("Running Stimulation Evoked Contractions, case 2")

        def param_changed(*args,val=True):
            param_has_changed = val

        class Row(tk.Frame):
            def __init__(self, parent, *args, **kwargs):
                tk.Frame.__init__(self, parent, *args, **kwargs)
                self.parent = parent
                self.root = tk.Frame(self.parent)
                self.is_string = False
                return
            
            def config(self, variable, value, comment, is_string):
                self.v_value = tk.StringVar(self.root)
                self.v_value.set(value)
                self.v_value.trace("w",param_changed)
                
                self.variable = variable
                self.comment = comment
                self.is_string = is_string
                
                frame = tk.Frame(self.root)
                var = tk.Label(frame, text=variable ,width=15,background='light gray')
                var.config(relief=tk.GROOVE)
                var.grid(column=0, row=0, padx=5, sticky='WE') 
                
                val = tk.Entry(frame,textvariable=self.v_value,width=40)
                val.grid(column=1, row=0, sticky='E')
                    
                CreateToolTip(var,comment)
                frame.pack()
                return self
            
            def row_to_param_str(self):
                #default_var("RunName","testrun")		// Name of simulation run
                proto = "default_var(\"{}\",{})\t\t// {}"
                if self.is_string:
                    proto = "default_var(\"{}\",\"{}\")\t\t// {}"
                line = proto.format(self.variable,self.v_value.get(),self.comment)
                return line

            def value(self):
                return self.v_value.get()
            
            def pack(self,*args,**kwargs):
                super(Row,self).pack(*args,**kwargs)
                self.root.pack(*args,**kwargs)
            
            def grid(self,*args,**kwargs):
                super(Row,self).grid(*args,**kwargs)
                self.root.grid(*args,**kwargs)

        """
        def refresh():
            param_changed(val=False)
            rows.clear()
            
            padtopbot = 3
            Row(general_frame).pack(pady=padtopbot-1)
            
            df = [
                ["Alpha Equation", "((v+45)/10)/(1-exp(-(v+45)/10))", "Alpha Equation", True],
                ["Beta Equation", "4*exp(-(v+70)/18)", "Beta Equation", True],
                ["Voltage Variable", "v", "Variable to plot", True],
            ]

            for i, row in enumerate(df):
                #config(self, variable, value, comment, is_string):
                frame=general_frame
                #This is all pages to change
                row = Row(frame).config(row[0],row[1],row[2],row[3])
                row.pack(padx=10)
                rows.append(row)
                #set_public_param(temp[0],row.v_value)
        
            Row(general_frame).pack(pady=padtopbot)
            return
        """

        #Membrane potential graph.
        self.alphagraph = Figure(figsize=(4,2), dpi=100)
        self.alphaplot = self.alphagraph.add_subplot(111)
        self.alphaplot.title.set_text('Alpha')
        #Create the canvas for the membrane vs time graph.
        self.alphacanvas = FigureCanvasTkAgg(self.alphagraph,top_option_frame)
        self.alphacanvas.draw()
        self.alphacanvas.get_tk_widget().grid(column = 0, row = 1)
        alphatoolbar_frame = tk.Frame(master=top_option_frame)
        alphatoolbar_frame.grid(column=0,row=0,sticky='w')
        alphatoolbar = NavigationToolbar2Tk(self.alphacanvas,alphatoolbar_frame)
        alphatoolbar.update()

        #Membrane potential graph.
        self.betagraph = Figure(figsize=(4,2), dpi=100)
        self.betaplot = self.betagraph.add_subplot(111)
        self.betaplot.title.set_text('Beta')
        #Create the canvas for the membrane vs time graph.
        self.betacanvas = FigureCanvasTkAgg(self.betagraph,top_option_frame)
        self.betacanvas.draw()
        self.betacanvas.get_tk_widget().grid(column = 0, row = 3)
        betatoolbar_frame = tk.Frame(master=top_option_frame)
        betatoolbar_frame.grid(column=0,row=2,sticky='w')
        betatoolbar = NavigationToolbar2Tk(self.betacanvas,betatoolbar_frame)
        betatoolbar.update()

        #Membrane potential graph.
        self.infgraph = Figure(figsize=(4,2), dpi=100)
        self.infplot = self.infgraph.add_subplot(111)
        self.infplot.title.set_text('Inf')
        #Create the canvas for the membrane vs time graph.
        self.infcanvas = FigureCanvasTkAgg(self.infgraph,top_option_frame)
        self.infcanvas.draw()
        self.infcanvas.get_tk_widget().grid(column = 1, row = 1)
        inftoolbar_frame = tk.Frame(master=top_option_frame)
        inftoolbar_frame.grid(column=1,row=0,sticky='w')
        inftoolbar = NavigationToolbar2Tk(self.infcanvas,inftoolbar_frame)
        inftoolbar.update()

        #Membrane potential graph.
        self.taugraph = Figure(figsize=(4,2), dpi=100)
        self.tauplot = self.taugraph.add_subplot(111)
        self.tauplot.title.set_text('Tau')
        #Create the canvas for the membrane vs time graph.
        self.taucanvas = FigureCanvasTkAgg(self.taugraph,top_option_frame)
        self.taucanvas.draw()
        self.taucanvas.get_tk_widget().grid(column = 1, row = 3)
        tautoolbar_frame = tk.Frame(master=top_option_frame)
        tautoolbar_frame.grid(column=1,row=2,sticky='w')
        tautoolbar = NavigationToolbar2Tk(self.taucanvas,tautoolbar_frame)
        tautoolbar.update()

        padtopbot = 3
        Row(general_frame).pack(pady=padtopbot-1)
        
    
        self.alpha_row = Row(general_frame).config("Alpha Equation", "((v+45)/10)/(1-exp(-(v+45)/10))", "Alpha Equation", True)
        self.alpha_row.pack(padx=10)

        self.beta_row = Row(general_frame).config("Beta Equation", "4*exp(-(v+70)/18)", "Beta Equation", True)
        self.beta_row.pack(padx=10)

        self.variable_row = Row(general_frame).config("Voltage Variable", "v", "Variable to plot", True)
        self.variable_row.pack(padx=10)
    
        Row(general_frame).pack(pady=padtopbot)

        plotButton = tk.Button(general_frame, text="Plot Equations", command=plot)
        #plotButton.grid(column=0, row =99, padx=5, pady=5, sticky='W')
        plotButton.pack()
        plotButton.config(state=tk.ACTIVE)

        """
        verifyBuildButton0 = tk.Button(general_frame, text="Run Custom Model", command=verify)
        #verifyBuildButton0.grid(column=0, row =99, padx=5, pady=5, sticky='W')
        verifyBuildButton0.pack()
        verifyBuildButton0.config(state=tk.DISABLED)

        verifyBuildButton = tk.Button(top_option_frame, text="Run Default Case", command=verify)
        verifyBuildButton.grid(column=1, row =0, padx=5, pady=5, sticky='W')
        verifyBuildButton.config(state=tk.ACTIVE)

        l = tk.Label(top_option_frame, text = "Normal functioning of bladder under constant fill rate with distension evoked contractions.")
        l.grid(column=2, row =0, padx=5, pady=5, sticky='W')

        verifyBuildButton1 = tk.Button(top_option_frame, text="Run Stimulation Case 1", command=verify1)
        verifyBuildButton1.grid(column=1, row =1, padx=5, pady=5, sticky='W')
        verifyBuildButton1.config(state=tk.ACTIVE)

        l1 = tk.Label(top_option_frame, text = "PUD stimulation at 70% maximum volume - PUD frequency: 33Hz, start 40000, stop 45000")
        l1.grid(column=2, row =1, padx=5, pady=5, sticky='W')

        verifyBuildButton2 = tk.Button(top_option_frame, text="Run Stimulation Case 2", command=verify2)
        verifyBuildButton2.grid(column=1, row =2, padx=5, pady=5, sticky='W')
        verifyBuildButton2.config(state=tk.ACTIVE)

        l1 = tk.Label(top_option_frame, text = "PUD stimulation at 40% maximum volume - PUD frequency: 33Hz, start 18000, stop 23000")
        l1.grid(column=2, row =2, padx=5, pady=5, sticky='W')

        """
        #refresh()

    def main(self):
        style = ttk.Style()
        try:
            style.theme_create( "colored", parent="alt", settings={
                    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                    "TNotebook.Tab": {
                        "configure": {"padding": [5, 2], "background": "#D9D9D9" },
                        "map":       {"background": [("selected", "#C0C0E0")],
                                    "expand": [("selected", [1, 1, 1, 0])] } } } )
        
            style.theme_create( "largertheme", parent="alt", settings={
                    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                    "TNotebook.Tab": {
                        "configure": {"padding": [5, 2] },
                        "map":       {
                                    "expand": [("selected", [1, 1, 1, 0])] } } } )
            style.theme_use("colored")
        except Exception:
            #print('Style loaded previously. Continuing.')
            pass
        
        frame1 = tk.Frame(self.root)
        frame1.grid(row=0,column=0,sticky='news')
        frame1.columnconfigure(0,weight=1)
        frame1.columnconfigure(0,weight=1)
        frame2 = tk.Frame(self.root)
        frame2.grid(row=1,column=0,sticky='news')
        
        nb = Autoresized_Notebook(frame1)
        nb.pack(padx=5,pady=5,side="left",fill="both",expand=True)
        
        bottom_status_bar = tk.Frame(frame2)
        bottom_status_bar.grid(row=0,column=0,padx=5,pady=2)#,fill=tk.X,expand=True)
        
        label = tk.Label(bottom_status_bar,textvariable=self.app_status)
        label.pack(expand=True)

        page1 = ttk.Frame(nb)
        
        nb.add(page1, text='Alpha/Beta to Inf/Tau')
        
        #Alternatively you could do parameters_page(page1), but wouldn't get scrolling
        self.bind_page(page1, self.parameters_page)
        
        self.display_app_status("Ready")
        try:
            #print('Load complete. Running Sim Builder...')
            self.root.mainloop()
        except Exception:
            print('Error, closing display loop')
        #print('Exiting')

    
    def reset_app_status(self):
        self.app_status.set(self.default_status)

    def display_app_status(self,str):
        self.app_status.set("Status: "+str)
        #threading.Timer(4.0, self.reset_app_status).start()
                
    