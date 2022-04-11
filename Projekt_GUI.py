#!/usr/bin/python
# -*- coding: utf-8 -*-
from Projekt import *
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as font
import string
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

global count_s
global count_v
global lst

rec_s = []
rec_v = []

root = Tk()
root.title('GUI')
root.geometry('705x540')


notebook = ttk.Notebook(root)
tab_1 = Frame(notebook, background='light goldenrod')
tab_2 = Frame(notebook)
tab_3 = Frame(notebook)

notebook.add(tab_1, text='Parametry')
notebook.add(tab_2, text='Mapa')
notebook.add(tab_3, text='Wykres')
notebook.pack(fill='both', expand=True)


def display_graph(result):
    for widget in tab_2.winfo_children():
        widget.destroy()
    fr = Frame(tab_2)
    fig = Figure(figsize=(7, 4), dpi=100)
    ax = fig.add_subplot(111)
    fr.pack(side=TOP, expand=True)  # if u want the toolbar higher!
    ax.scatter(0, 0, label='Bakery')
    for i in range(len(vehicles)):
        x = []
        y = []
        num = np.linspace(1, len(result[1].get(i + 1)), len(result[1].get(i + 1)))
        name = []
        for j in range(len(result[1].get(i + 1))):
            x.append(result[0][vehicles[i]][j].get_position()[0])
            y.append(result[0][vehicles[i]][j].get_position()[1])
            name.append(result[0][vehicles[i]][j].get_name())
        ax.scatter(x, y, label='Vehicle {}'.format(i + 1))
        for k in range(len(y)):
            ax.annotate((num[k], name[k]), (x[k], y[k]), fontsize=7)
    ax.annotate('Bakery', (0, 0), fontsize=7)
    ax.set_xlabel('Współrzędna x')
    ax.set_ylabel('Współrzędna y')
    ax.set_title('Mapa sklepów i piekarni')
    scatter = FigureCanvasTkAgg(fig, tab_2)
    scatter.draw()
    scatter.get_tk_widget().pack(expand=True, fill='both')
    ax.legend(loc='lower left')

    toolbar = NavigationToolbar2Tk(scatter, fr)

    toolbar.update()

    scatter.get_tk_widget().pack(expand=True, fill='both')


def plot_figure(result):
    for widget in tab_3.winfo_children():
        widget.destroy()

    fr = Frame(tab_3)
    fig = Figure(figsize=(5, 4))

    x = np.linspace(1, result[4], num=result[4])
    y = result[5]

    plot1 = fig.add_subplot(111)

    plot1.plot(x, y, label='Funkcja celu')
    plot1.scatter(int(result[3]), result[2], label='Najlepsze rozwiązanie', color='red')
    plot1.legend(loc='lower right')
    plot1.set_ylabel('Wartość funkcji celu')
    plot1.set_xlabel('Numer iteracji')
    plot1.set_title('Przebieg funkcji celu dla każdej iteracji')
    fr.pack(side=TOP, expand=True)  # if u want the toolbar higher!

    canvas = FigureCanvasTkAgg(fig, master=tab_3)
    canvas.draw()

    canvas.get_tk_widget().pack(expand=True, fill='both')

    toolbar = NavigationToolbar2Tk(canvas, fr)

    toolbar.update()

    canvas.get_tk_widget().pack(expand=True, fill='both')

    results = Frame(tab_3)
    results.pack(expand=True, side=BOTTOM)
    Label(results, text='Najlepsze rozwiązanie: {}    Znaleziono w {}. iteracji    Długość listy tabu: {}    '
                        'Ilość wszystkich iteracji: {}'.format(result[2], result[3], int(row_11.get()), result[4])).pack()
    Label(results, text='Samochody z listą sklepów: {} '.format(result[1])).pack()



def run_project():
    result = bakery.tabu_search_2()
    plot_figure(result)
    display_graph(result)


def is_correct_hour(line: str):
    if re.fullmatch(r'2[0-4]' + ':' + r'[0-5][0-9]', line) or re.fullmatch(r'[0-1][0-9]' + ':' + r'[0-5][0-9]', line) \
            or re.fullmatch(r'[0-9]' + ':' + r'[0-5][0-9]', line):
        return True
    else:
        return False


def str_to_int(line: str):
    zm = line.split(':')
    return [int(zm[0]), int(zm[1])]


def delete_shop(my_tree):
    global count_s
    global rec_s
    x = my_tree.selection()
    c = 0
    rec = []
    for record in x:
        my_tree.delete(record)
        rec.append(int(record))
        c += 1
    count_s -= c
    rec_s = rec_s + rec
    rec_s = sorted(rec_s, reverse=True)


def add_shop(my_tree, nr, x, y, hour, m, z, p):
    if (x.get().isdigit() or (x.get().find('-') == 0 and x.get().replace('-', '', 1).isdigit()) or
        (x.get().find('.') != 0 and x.get().find('.') != -1 and x.get().replace('.', '', 1).isdigit()) or
        (x.get().find('-') == 0 and x.get().find('.') != 1 and x.get().find('.') != -1 and
         x.get().replace('.', '', 1).replace('-', '', 1).isdigit())) and \
            (y.get().isdigit() or (y.get().find('-') == 0 and y.get().replace('-', '', 1).isdigit()) or
             (y.get().find('.') != 0 and y.get().find('.') != -1 and y.get().replace('.', '', 1).isdigit()) or
             (y.get().find('-') == 0 and y.get().find('.') != 1 and y.get().find('.') != -1 and
              y.get().replace('.', '', 1).replace('-', '', 1).isdigit())) and \
            m.get().isdigit() and z.get().isdigit() and p.get().isdigit() and is_correct_hour(hour.get()):
        global count_s
        global lst
        if (int(x.get()), int(y.get())) not in lst:
            my_tree.insert(parent='', index='end', iid=count_s, text='{}'.format(count_s + 1),
                           values=(nr.get(), x.get(), y.get(), m.get(), z.get(), p.get(), hour.get()))
            count_s += 1
            hours = str_to_int(hour.get())
            shop = Shop(nr.get(), int(x.get()), int(y.get()), int(m.get()), int(z.get()), int(p.get()), hours)
            shops.append(shop)
            bakery.set_shops(shops)
            lst.append((int(x.get()), int(y.get())))
            nr.delete(0, END)
            x.delete(0, END)
            y.delete(0, END)
            hour.delete(0, END)
            m.delete(0, END)
            z.delete(0, END)
            p.delete(0, END)
        else:
            messagebox.showinfo('Alert', 'Zajęte współrzędne!')
    else:
        messagebox.showinfo('Alert', 'Źle wpisane wartości!')


def shop_exit(top):
    global rec_s
    for i in range(len(rec_s)):
        shops.pop(int(rec_s[i]))
        lst.pop(int(rec_s[i]))
    bakery.set_shops(shops)
    rec_s = []
    top.destroy()


def delete_vehicle(my_tree):
    global count_v
    global rec_v
    x = my_tree.selection()
    c = 0
    rec = []
    for record in x:
        my_tree.delete(record)
        rec.append(int(record))
        c += 1
    count_v -= c
    rec_v = rec_v + rec
    rec_v = sorted(rec_v, reverse=True)


def add_vehicle(my_tree, nr, vel, cap, comb):
    if vel.get().replace('.', '', 1).isdigit() and cap.get().isdigit() and comb.get().replace('.', '', 1).isdigit():
        global count_v
        velocity = float(vel.get())
        combustion = float(comb.get())
        my_tree.insert(parent='', index='end', iid=count_v, text='{}'.format(count_v + 1), values=(nr.get(), velocity,
                                                                                                   cap.get(), combustion))
        count_v += 1
        vehicle = Vehicle(int(nr.get()), float(vel.get()), int(cap.get()), float(comb.get()))
        vehicles.append(vehicle)
        bakery.set_cars(vehicles)
        nr.delete(0, END)
        vel.delete(0, END)
        cap.delete(0, END)
        comb.delete(0, END)
    else:
        messagebox.showinfo('Alert', 'Źle wpisane wartości!')


def vehicle_exit(top):
    global rec_v
    for i in range(len(rec_v)):
        vehicles.pop(int(rec_v[i]))
    bakery.set_cars(vehicles)
    rec_v = []
    top.destroy()


def change_shop():
    global count_s
    global lst
    top = Toplevel()
    top.title('Edycja sklepów')
    top.geometry('500x500')

    tree_frame = Frame(top)
    tree_scroll_y = Scrollbar(tree_frame)
    tree_scroll_y.pack(side=RIGHT, fill=Y)
    tree_scroll_x = Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side=BOTTOM, fill=X)
    tree_frame.pack(pady=10)

    words = ['Nazwa', 'Położenie X', 'Położenie Y', 'Potrzebne chleby mieszane', 'Potrzebne chleby żytnie',
             'Potrzebne chleby pszenne', 'Docelowa godzina przyjazdu']
    my_tree = ttk.Treeview(tree_frame, xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)
    my_tree['columns'] = words
    my_tree.column('#0', width=100, anchor=CENTER)
    my_tree.heading('#0', text='Numer obiektu')
    for i in range(len(words)):
        my_tree.column(words[i], width=155, anchor=CENTER)
        my_tree.heading(words[i], text=words[i])
    count_s = 0

    lst = [(0, 0)]
    for record in shops:
        my_tree.insert(parent='', index='end', iid=count_s, text='{}'.format(count_s + 1),
                       values=(record.get_name(), record.get_position()[0], record.get_position()[1],
                               record.get_needs()[0], record.get_needs()[1], record.get_needs()[2], record.get_hour()))
        count_s += 1
        lst.append(record.get_position())
    my_tree.pack()
    tree_scroll_y.config(command=my_tree.yview)
    tree_scroll_x.config(command=my_tree.xview)

    entry_frame_1 = Frame(top)
    name_lb_1 = Label(entry_frame_1, text='Nazwa')
    name_lb_1.grid(row=0, column=0)
    name_en_1 = Entry(entry_frame_1)
    name_en_1.grid(row=1, column=0)

    name_lb_2 = Label(entry_frame_1, text='Położenie X')
    name_lb_2.grid(row=0, column=1)
    name_en_2 = Entry(entry_frame_1)
    name_en_2.grid(row=1, column=1)

    name_lb_3 = Label(entry_frame_1, text='Położenie Y')
    name_lb_3.grid(row=0, column=2)
    name_en_3 = Entry(entry_frame_1)
    name_en_3.grid(row=1, column=2)

    name_lb_4 = Label(entry_frame_1, text='Godzina przyjazdu')
    name_lb_4.grid(row=0, column=3)
    name_en_4 = Entry(entry_frame_1)
    name_en_4.grid(row=1, column=3)
    entry_frame_1.pack(pady=5)

    entry_frame_2 = Frame(top)
    name_lb_5 = Label(entry_frame_2, text='Chleby mieszane')
    name_lb_5.grid(row=0, column=0)
    name_en_5 = Entry(entry_frame_2)
    name_en_5.grid(row=1, column=0)

    name_lb_6 = Label(entry_frame_2, text='Chleby żytnie')
    name_lb_6.grid(row=0, column=1)
    name_en_6 = Entry(entry_frame_2)
    name_en_6.grid(row=1, column=1)

    name_lb_7 = Label(entry_frame_2, text='Chleby pszenne')
    name_lb_7.grid(row=0, column=2)
    name_en_7 = Entry(entry_frame_2)
    name_en_7.grid(row=1, column=2)
    entry_frame_2.pack(pady=5)

    button_frame = Frame(top)
    add_button = Button(button_frame, text="Dodaj sklep", command=lambda: add_shop(my_tree, name_en_1, name_en_2,
                                                                                   name_en_3, name_en_4, name_en_5,
                                                                                   name_en_6, name_en_7))
    add_button.grid(row=0, column=0, padx=20, pady=5)
    delete_button = Button(button_frame, text="Usuń sklep", command=lambda: delete_shop(my_tree))
    delete_button.grid(row=0, column=1, padx=20, pady=5)
    finish_button = Button(button_frame, text='Zatwierdź i zakończ', command=lambda: shop_exit(top))
    finish_button.grid(row=0, column=2, padx=20, pady=5)
    button_frame.pack(pady=5)


def change_vehicle():
    global count_v
    top = Toplevel()
    top.title('Edycja sklepów')
    top.geometry('500x500')

    tree_frame = Frame(top)
    tree_scroll_y = Scrollbar(tree_frame)
    tree_scroll_y.pack(side=RIGHT, fill=Y)
    tree_scroll_x = Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side=BOTTOM, fill=X)
    tree_frame.pack(pady=10)

    words = ['Nazwa', 'Prędkość [km/h]', 'Pojemność', 'Spalanie [L/100km]']
    my_tree = ttk.Treeview(tree_frame, xscrollcommand=tree_scroll_x.set, yscrollcommand=tree_scroll_y.set)
    my_tree['columns'] = words
    my_tree.column('#0', width=100, anchor=CENTER)
    my_tree.heading('#0', text='Numer obiektu')
    for i in range(len(words)):
        my_tree.column(words[i], width=150, anchor=CENTER)
        my_tree.heading(words[i], text=words[i])
    count_v = 0

    for record in vehicles:
        zm = record.get_parameters()
        velocity = zm[1] * 6 / 100
        combustion = zm[3] * 100000
        my_tree.insert(parent='', index='end', iid=count_v, text='{}'.format(count_v + 1),
                       values=(zm[0], velocity, zm[2], combustion))
        count_v += 1
    my_tree.pack()
    tree_scroll_y.config(command=my_tree.yview)
    tree_scroll_x.config(command=my_tree.xview)

    entry_frame_1 = Frame(top)
    name_lb_1 = Label(entry_frame_1, text='Nazwa')
    name_lb_1.grid(row=0, column=0)
    name_en_1 = Entry(entry_frame_1)
    name_en_1.grid(row=1, column=0)

    name_lb_2 = Label(entry_frame_1, text='Prędkość')
    name_lb_2.grid(row=0, column=1)
    name_en_2 = Entry(entry_frame_1)
    name_en_2.grid(row=1, column=1)

    name_lb_3 = Label(entry_frame_1, text='Pojemność')
    name_lb_3.grid(row=0, column=2)
    name_en_3 = Entry(entry_frame_1)
    name_en_3.grid(row=1, column=2)

    name_lb_4 = Label(entry_frame_1, text='Spalanie')
    name_lb_4.grid(row=0, column=3)
    name_en_4 = Entry(entry_frame_1)
    name_en_4.grid(row=1, column=3)
    entry_frame_1.pack(pady=5)

    button_frame = Frame(top)
    add_button = Button(button_frame, text="Dodaj pojazd", command=lambda: add_vehicle(my_tree, name_en_1, name_en_2,
                                                                                       name_en_3, name_en_4))
    add_button.grid(row=0, column=0, padx=20, pady=5)
    delete_button = Button(button_frame, text="Usuń pojazd", command=lambda: delete_vehicle(my_tree))
    delete_button.grid(row=0, column=1, padx=20, pady=5)
    finish_button = Button(button_frame, text='Zatwierdź i zakończ', command=lambda: vehicle_exit(top))
    finish_button.grid(row=0, column=2, padx=20, pady=5)
    button_frame.pack(pady=5)


def change_bakery(wm, wz, wp, goal, size, max_it):
    if wm.get().replace('.', '', 1).isdigit() and wz.get().replace('.', '', 1).isdigit() and \
            wp.get().replace('.', '', 1).isdigit() and goal.get().replace('.', '', 1).isdigit() and \
            size.get().isdigit() and max_it.get().isdigit():
        bakery.set_parameters(float(wm.get()), float(wz.get()), float(wp.get()), float(goal.get()), int(size.get()),
                              int(max_it.get()))
        messagebox.showinfo('Alert', 'Zaktualizowano zmienne!')
    else:
        messagebox.showinfo('Alert', 'Źle wpisane wartości!')

frame_0 = Frame(tab_1, background='light goldenrod')
frame_0.pack(expand=True)
min_fram = Frame(frame_0,pady=5, background='light goldenrod')
min_fram.grid(row=0, column=0,padx=200)
ddd = Label(min_fram, text='Problem logistyczny piekarni', font=('Comic Sans MS', 19), fg='Green', pady=11, background='light goldenrod')
ddd.pack(expand=True)

frame_1 = Frame(tab_1, background='light goldenrod')
frame_1.pack(expand=True)

Grid.columnconfigure(tab_1, 0, weight=1)

change_shops = Button(frame_1, text="Edycja sklepów", command=change_shop, bg='gold2', padx=30)
change_shops.grid(row=1, column=0, padx=55)
change_shops['font'] = font.Font(size=12)
change_vehicles = Button(frame_1, text="Edycja pojazdów", command=change_vehicle, bg='gold2', padx=25)
change_vehicles.grid(row=1, column=1, padx=35)
change_vehicles['font'] = font.Font(size=12)

frame_2 = Frame(tab_1, background='light goldenrod')
frame_2.pack(expand=True)
parameters = bakery.get_parameters()

min_frame_00 = Frame(frame_2, padx=25, pady=25, background='light goldenrod')
min_frame_00.grid(row=1, column=0, padx=5, pady=5)
T_00 = Label(min_frame_00, text='Cena chlebów mieszanych', background='light goldenrod')
T_00['font'] = font.Font(size=11)
T_00.pack(expand=True)
row_00 = Entry(min_frame_00)
row_00['font'] = font.Font(size=11)
row_00.insert(0, parameters[0])
row_00.pack(expand=True)

min_frame_10 = Frame(frame_2, background='light goldenrod')
min_frame_10.grid(row=2, column=0, padx=5, pady=5)
T_10 = Label(min_frame_10, text='Cena chlebów żytnich', background='light goldenrod')
T_10['font'] = font.Font(size=11)
T_10.pack(expand=True)
row_10 = Entry(min_frame_10)
row_10['font'] = font.Font(size=11)
row_10.insert(0, parameters[1])
row_10.pack(expand=True)

min_frame_20 = Frame(frame_2, padx=25, pady=25, background='light goldenrod')
min_frame_20.grid(row=3, column=0, padx=5, pady=5)
T_20 = Label(min_frame_20, text='Cena chlebów pszennych', background='light goldenrod')
T_20['font'] = font.Font(size=11)
T_20.pack(expand=True)
row_20 = Entry(min_frame_20)
row_20['font'] = font.Font(size=11)
row_20.insert(0, parameters[2])
row_20.pack(expand=True)

min_frame_01 = Frame(frame_2, padx=25, pady=25, background='light goldenrod')
min_frame_01.grid(row=1, column=1, padx=5, pady=5)
T_01 = Label(min_frame_01, text='Zadowalający zysk', background='light goldenrod')
T_01['font'] = font.Font(size=11)
T_01.pack(expand=True)
row_01 = Entry(min_frame_01)
row_01['font'] = font.Font(size=11)
row_01.insert(0, parameters[3])
row_01.pack(expand=True)

min_frame_11 = Frame(frame_2, background='light goldenrod')
min_frame_11.grid(row=2, column=1, padx=5, pady=5)
T_11 = Label(min_frame_11, text='Długość listy tabu', background='light goldenrod')
T_11['font'] = font.Font(size=11)
T_11.pack(expand=True)
row_11 = Entry(min_frame_11)
row_11['font'] = font.Font(size=11)
row_11.insert(0, parameters[4])
row_11.pack(expand=True)

min_frame_21 = Frame(frame_2, padx=25, pady=25, background='light goldenrod')
min_frame_21.grid(row=3, column=1, padx=5, pady=5)
T_21 = Label(min_frame_21, text='Ilość iteracji', background='light goldenrod')
T_21['font'] = font.Font(size=11)
T_21.pack(expand=True)
row_21 = Entry(min_frame_21)
row_21['font'] = font.Font(size=11)
row_21.insert(0, parameters[5])
row_21.pack(expand=True)

update_variables = Button(frame_2, text="Aktualizacja zmienych", bg='gold2', command=lambda: change_bakery(row_00, row_10, row_20, row_01, row_11, row_21))
update_variables.grid(row=4, column=0, padx=10, pady=5, columnspan=2)
update_variables['font'] = font.Font(size=11)

frame_3 = Frame(tab_1, background='light goldenrod')
frame_3.pack(expand=True)

run_project = Button(frame_3, text="Uruchom program", command=run_project, bg='gold2', padx=30)
run_project.grid(row=0, column=0, padx=55, pady=30)
run_project['font'] = font.Font(size=12)
close_window = Button(frame_3, text="Zamknij aplikację", command=lambda: root.destroy(), bg='orange red', padx=25)
close_window.grid(row=0, column=1, padx=35, pady=30)
close_window['font'] = font.Font(size=12)

root.mainloop()
