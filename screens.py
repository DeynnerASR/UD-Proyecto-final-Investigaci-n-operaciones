import tkinter as tk
from constantes import style, config
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import symbols, Eq, solve, sympify
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import json 
import re



class Principal(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background = style.BACKGROUND )
        self.controller = controller

        self.__init__widgets()

    def Pestaña_inputs_mg(self):
        self.controller.show_frame(Inputs_metodo_grafico)

    def __init__widgets(self):
        tk.Button(
            self,
            text="Método Gráfico",
            justify = "center",
            command = self.Pestaña_inputs_mg,
            **style.STYLE
        ).pack(
            side = tk.TOP,
            fill= tk.BOTH, 
            padx = 20,
            pady = 20,
        )


class Inputs_metodo_grafico(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background=style.BACKGROUND)
        self.controller = controller
        self.MinMaxtype = tk.StringVar(self, value="Maximo")
        self.Metodo = tk.StringVar(self, value="Grafico")

        self.result_panel = None

        # Configurar canvas y scrollbar
        self.canvas = tk.Canvas(self, background=style.BACKGROUND)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background=style.BACKGROUND)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empacar canvas y scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.__init__widgets()

        # Lista para almacenar los widgets generados
        self.entry_widgets = []
        self.warning_message_widget = None
        self.continue_button = None
        self.warning_entry_mg = None
        self.warning_entry_ob = None
        self.warning_entry_res = None

    

    def realizarPeticion(self):
        print("Realizando petición HTTP")

        # URL a la que se enviará la petición
        url = 'https://graphicalmethodapi-dmd3bca6e6dpenev.canadacentral-01.azurewebsites.net/graphical-method/solve'

        # Datos que se enviarán en el cuerpo de la petición
        funcion_objetivo = self.ob.get()  # La función objetivo ingresada por el usuario
        funcion_objetivo = re.sub(r'x1', 'x', re.sub(r'x2', 'y', funcion_objetivo))
        tipo = self.MinMaxtype.get() == "Maximo"  # Tipo de optimización (Maximizar o Minimizar)
        # Convertir variables x1, x2, etc., a x, y, etc., en las restricciones
        lista_restricciones_texto = [re.sub(r'x1', 'x', re.sub(r'x2', 'y', widget.get())) for widget in self.entry_widgets]

        print("funcion objetivo transformada:", funcion_objetivo)
        print("Restricciones transformadas:", lista_restricciones_texto)

        # Preparar los datos para la solicitud
        data = {
            "objectiveFunctionText": funcion_objetivo,
            "restrictionsText": lista_restricciones_texto,
            "isMaximization": tipo
        }

        print ('Body de la peticion : ',data)

        # Realizar la petición POST
        respuesta = requests.post(url, json=data)

        
        # Imprimir la respuesta del servidor
        if respuesta.status_code == 200:
            resultado = respuesta.json();
            print("Petición realizada con éxito:", resultado)
            self.mostrar_resultados(resultado)
        else:
            print("Error en la petición:", respuesta.status_code, respuesta.text)

    def mostrar_resultados(self, resultado):
        
        if not self.result_panel:
            # Crear el panel si no existe
            self.result_panel = tk.Text(self.scrollable_frame, height=10, wrap="word")
            self.result_panel.pack(fill="x", padx=10, pady=10)
            self.result_panel.config(state="disabled")  # Hacer no editable

        # Actualizar contenido
        tipo_funcion = self.MinMaxtype.get()

        self.result_panel.config(state="normal")  # Permitir edición temporal
        self.result_panel.delete(1.0, tk.END)  # Limpiar contenido previo
        self.result_panel.insert(tk.END, f"Resultados:\nIntersecciones:\n")  # Agregar datos        
        for point in resultado['intersections']:
            print(f"x: {point['x']}, y: {point['y']}")
            self.result_panel.insert(tk.END, f"x: {point['x']}, y: {point['y']}) \n");
        

        intersecciones = resultado['intersections']
        

        if tipo_funcion == 'Maximo':
                
            indice = resultado['maxIndex']
            self.result_panel.insert(tk.END, f"Puntos de la solucion : {intersecciones[indice]}")  
            self.result_panel.insert(tk.END, f"\nValor maximo:{resultado['maxValue']}")  # Agregar datos                    
        else:
            indice = resultado['minIndex']
            self.result_panel.insert(tk.END, f"Puntos de la solucion : {intersecciones[indice]}")  
            self.result_panel.insert(tk.END, f"\nValor minimo:{resultado['minValue']}")  # Agregar datos        
        #if tipo = "Maximo":
                
        self.result_panel.config(state="disabled")  # Volver a deshabilitar

    # Funcion la cual se va a ejecutar cuando presione el boton continuar
    def Proceso_mg(self):
        if (self.revision_f() == False):
            return

        self.controller.tipo = self.MinMaxtype.get()
        self.Cx1 = []
        self.Cx2 = []
        #self.controller.show_frame(Metodo_grafico)
        """
        tk.Label(
            self.scrollable_frame,
            text = self.MinMaxtype.get() + "/" + self.Metodo.get()
        ).pack(
            side = tk.TOP,
            padx = 5,
            pady = 5
        )

        for widget in self.entry_widgets:
            tk.Label(
                self.scrollable_frame,
                text = widget.get()
            ).pack(
                side = tk.TOP,
                padx = 5,
                pady = 5
            )
        """

        funcion_objetivo = self.ob.get()
        print(f'Función objetivo: {funcion_objetivo}')
        
        # Imprimir la cantidad de variables
        cantv = int(self.cantv.get())
        print(f'Cantidad de variables: {cantv}')

        self.realizarPeticion()

        # Imprimir cada restricción ingresada
        for i, widget in enumerate(self.entry_widgets, start=1):
            restriccion = widget.get()
            print(f'Restricción {i}: {restriccion}')

        #En este punto debo enviar los datos a la appi

        if self.Metodo.get() == "Grafico":
            x1, x2 = sp.symbols('x1 x2')
            funcion_objetivo = self.ob.get()

            for widget in self.entry_widgets:
                lhs_str, rhs_str = widget.get().split('=')    
                
                lhs_1 = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', lhs_str)
                rhs_1 = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', rhs_str)

                lhs = sympify(lhs_1.strip())
                rhs = sympify(rhs_1.strip())


                #restriccion = sp.Eq(lhs, rhs)
                restriccion = sp.Eq(lhs, rhs)
                corte_x1 = sp.solve(restriccion.subs(x2, 0), x1)
                corte_x2 = sp.solve(restriccion.subs(x1, 0), x2)
                self.Cx1.append(corte_x1 if corte_x1 else [0])
                self.Cx2.append(corte_x2 if corte_x2 else [0])
            
            """
            print("Elementos de corte_x1:")
            for elemento in self.Cx1:
                print(elemento)
    
            print("\nElementos de corte_x2:")
            for elemento in self.Cx2:
                print(elemento)

            """

            fig, ax = plt.subplots()
        
            # Configurar limites de los ejes
            ax.set_xlim(0, max([float(val[0]) for val in self.Cx1 if val]))
            ax.set_ylim(0, max([float(val[0]) for val in self.Cx2 if val]))
        
            # Graficar cada restriccion
            for x1_val, x2_val in zip(self.Cx1, self.Cx2):
                if x1_val and x2_val:
                    x_vals = [0, float(x1_val[0])]
                    y_vals = [float(x2_val[0]), 0]
                    ax.plot(x_vals, y_vals, label=f"x1: {x1_val[0]}, x2 : {x2_val[0]}", alpha=0.2)
                if x1_val[0] == 0:
                    plt.axvline(x2_val)
                if x2_val[0] == 0:
                    plt.axhline(x1_val)
                
        
            ax.legend()
            ax.set_xlabel("x1")
            ax.set_ylabel("x2")
            ax.set_title("Método Gráfico - Restricciones")

            if hasattr(self, 'graph_frame') and self.graph_frame:
                self.graph_frame.destroy()
            

            self.graph_frame = tk.Frame(self.canvas, background=style.BACKGROUND)
            self.graph_frame.pack(side = tk.RIGHT, anchor="ne")

            canvas = FigureCanvasTkAgg(fig, master = self.graph_frame)
            canvas.get_tk_widget().pack(anchor="n", padx=5, pady=5)
            canvas.draw()
        
            #if self.MinMaxtype.get() == "Maximo":


            #if self.MinMaxtype.get() == "Minimo":

            
        #if self.Metodo.get() == "Dos":


    def limpiar_entradas(self):
        # Elimina cada widget de entrada almacenado
        for widget in self.entry_widgets:
            widget.destroy()
        self.entry_widgets.clear()

        # Elimina el botón "Continuar" si existe
        if self.continue_button:
            self.continue_button.destroy()
            self.continue_button = None

        if self.warning_message_widget:
            self.warning_message_widget.destroy()
            self.warning_message_widget = None 

        if self.warning_entry_mg:
            self.warning_entry_mg.destroy()
            self.warning_entry_mg = None

        if self.warning_entry_ob:
            self.warning_entry_ob.destroy()
            self.warning_entry_ob = None
        
        if self.warning_entry_res:
            self.warning_entry_res.destroy()
            self.warning_entry_res = None

    def Restricciones_intp(self):
        # Limpia los widgets de entrada previos
        self.limpiar_entradas()

        cantv = int(self.cantv.get())
        cant_res = int(self.cant_res.get())

        print(cantv)
        print(cant_res)

# Aqui agrega las restricciones y el boton continar para el metodo grafico, teniendo en cuenta los siguientes datos
        # cantv (cantidad de variables) sea igual a 2
        # metodo (sea igual a "Grafico")
        # cant_res (cantidad de restricciones) sea mayor a 0
        if (cantv == 2 and self.Metodo.get() == "Grafico" and cant_res > 0):
            for i in range(cant_res):
                restriccion_var = tk.StringVar(self)
                self.restricciones.append(restriccion_var)

                entry = tk.Entry(self.scrollable_frame, textvariable = restriccion_var)
                entry.pack(pady=5)
                # Añadir a la lista de widgets
                self.entry_widgets.append(entry)

            # Agregar el botón "Continuar" si no existe
            self.Continuar_button()

        elif (self.Metodo.get() == "Grafico"):
            self.Condicional_max()  

# Aqui agrega las restricciones y el boton continar para el metodo de dos fases, teniendo en cuenta los siguientes datos
        # cantv (cantidad de variables) sea igual a 2
        # metodo (sea igual a "Grafico")
        # cant_res (cantidad de restricciones) sea mayor a 0
        if (cantv > 0 and cantv <=15 and self.Metodo.get() == "Dos" and cant_res > 0):
            for i in range(cant_res):
                restriccion_var = tk.StringVar(self)
                self.restricciones.append(restriccion_var)

                entry = tk.Entry(self.scrollable_frame, textvariable = restriccion_var)
                entry.pack(pady=5)
                # Añadir a la lista de widgets
                self.entry_widgets.append(entry)

            # Agregar el botón "Continuar" si no existe
            self.Continuar_button()

        elif (self.Metodo.get() == "Dos"):
            self.Create_warning()
        

    def Create_warning(self):
        if not self.warning_message_widget:
            self.warning_message_widget = tk.Label(
                self.scrollable_frame,
                text="Deben ser entre 1 a 15 variables para el metodo\ny 1 o más restricciones",
                justify="center",
                **style.STYLE
            )
            self.warning_message_widget.pack(
                side=tk.TOP,  
                padx=5, 
                pady=5
            )
        
    def Condicional_max(self):
        if not self.warning_entry_mg:
            self.warning_entry_mg = tk.Label(
                self.scrollable_frame,
                text = "Deben ser 2 variables para el metodo grafico\ny 1 o más restricciones",
                justify="center",
                **style.STYLE  
            )
            self.warning_entry_mg.pack(
                side=tk.TOP,  
                padx=5, 
                pady=5
            )

    def Campo_ob(self):
        if not self.warning_entry_ob:
            self.warning_entry_ob = tk.Button(
                self.scrollable_frame,
                text = "Debes llenar el campo de funcion objetivo",
                justify="center",
                **style.STYLE  
            )
            self.warning_entry_ob.pack(
                side=tk.TOP,  
                padx=5, 
                pady=5
            )

    def Campo_res(self):
        if not self.warning_entry_res:
            self.warning_entry_res= tk.Button(
                self.scrollable_frame,
                text = "Debes llenar todos los campos de restricciones",
                justify="center",
                **style.STYLE  
            )
            self.warning_entry_res.pack(
                side=tk.TOP,  
                padx=5, 
                pady=5
            )

    def revision_f(self):
        cantv = int(self.cantv.get())
        cant_res = int(self.cant_res.get())

        if ((cantv != 2 or cant_res < 1) and self.Metodo.get() == "Grafico"):
            self.limpiar_entradas()
            self.Condicional_max()
            return False

        if ((cantv < 0 or cantv > 15 or cant_res < 1) and self.Metodo.get() == "Dos"):
            self.limpiar_entradas()
            self.Create_warning()
            return False
        
        if (self.ob.get() == ''):
            self.limpiar_entradas()
            self.Campo_ob()
            return False

        for widget in self.entry_widgets:
            if (widget.get() == ''):
                self.limpiar_entradas()
                self.Campo_res()
                return False

        return True

    def Continuar_button(self):
        # Crear el boton "Continuar" solo si aun no existe
        if not self.continue_button:
            self.continue_button = tk.Button(
                self.scrollable_frame,
                text="Continuar",
                justify="center",
                command=self.Proceso_mg,
                **style.STYLE,
                relief=tk.FLAT,
                activebackground=style.BACKGROUND,
                activeforeground=style.TEXT,
            )
            self.continue_button.pack(
                side=tk.TOP, 
                fill=tk.X, 
                padx=20, 
                pady=20
            )

    def __init__widgets(self):
        self.cantv = tk.IntVar(self)
        self.ob = tk.StringVar(self)
        self.cant_res = tk.IntVar(self)
        self.restricciones = []

        tk.Label(self)
        optionsFrame = tk.Frame(self)
        optionsFrame.configure(background=style.COMPONENT)
        optionsFrame.pack(side=tk.TOP, fill=tk.BOTH, padx=20, pady=20)

        tk.Label(
            self.scrollable_frame,
            text="Elegir el metodo",
            justify=tk.CENTER,
            **style.STYLE
        ).pack(
            side=tk.TOP,
            fill=tk.X, 
            padx=5, 
            pady=5,
        )

        for (key, value) in config.METODOS.items():
            tk.Radiobutton(
                self.scrollable_frame,
                text=key,
                variable=self.Metodo,
                value=value,
                activebackground=style.BACKGROUND,
                activeforeground=style.TEXT,
                justify=tk.CENTER,
                **style.STYLE
            ).pack(
                side=tk.TOP, 
                padx=5, 
                pady=5
            )

        tk.Label(self)
        optionsFrame = tk.Frame(self)
        optionsFrame.configure(background=style.COMPONENT)
        optionsFrame.pack(side=tk.TOP, fill=tk.BOTH, padx=20, pady=20)

        tk.Label(
            self.scrollable_frame,
            text="Elegir la opción de la función objetivo",
            justify=tk.CENTER,
            **style.STYLE
        ).pack(
            side=tk.TOP,
            fill=tk.X, 
            padx=5, 
            pady=5
        )

        for (key, value) in config.OPCIONES.items():
            tk.Radiobutton(
                self.scrollable_frame,
                text=key,
                variable=self.MinMaxtype,
                value=value,
                activebackground=style.BACKGROUND,
                activeforeground=style.TEXT,
                justify=tk.CENTER,
                **style.STYLE
            ).pack(
                side=tk.TOP, 
                padx=5, 
                pady=5
            )

        tk.Label(
            self.scrollable_frame,
            text="Ingrese la cantidad de variables",
            justify="center",
        ).pack(
            pady=5
        )

        tk.Entry(
            self.scrollable_frame,
            textvariable = self.cantv
            ).pack(
                pady=5
        )

        tk.Label(
            self.scrollable_frame,
            text="Ingrese la función objetivo",
            justify="center",
        ).pack(
            pady=5
        )

        tk.Entry(
            self.scrollable_frame,
            textvariable = self.ob
            ).pack(
                pady=5
        )

        tk.Label(
            self.scrollable_frame,
            text="Ingrese el número de restricciones",
            justify="center",
        ).pack(
            pady=5
        )

        tk.Entry(
            self.scrollable_frame,
            textvariable = self.cant_res
        ).pack(
            pady=5
        )

        tk.Button(
            self.scrollable_frame,
            text="Generar",
            **style.STYLE,
            command=self.Restricciones_intp,
            activebackground=style.BACKGROUND,
            activeforeground=style.TEXT,
        ).pack(
            side=tk.TOP, 
            padx=5, 
            pady=5
        )

        

"""
class Metodo_grafico(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background = style.BACKGROUND )
        self.controller = controller

        self.__init__widgets()

    def __init__widgets(self):
        tk.Label(
            self,
            text="Método Gráfico Resultado",
            justify = "center",
            **style.STYLE
        ).pack(
            side = tk.TOP,
            fill= tk.BOTH, 
            padx = 20,
            pady = 20,
        )

class Metodo_(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background = style.BACKGROUND )
        self.controller = controller

"""