class F:

    def read(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            for linea in f:
                print(linea.strip())

    def write(self, filename, dictionary, add_id_name):
        enable = 1
        id = 1
        with open(filename, "w", encoding="utf-8") as f:
            labels = list(dictionary[0].keys())
            f.write(add_id_name + ",")
            for label in labels:
                f.write(label + ",")
            f.write("activo\n")
            for a in dictionary:
                f.write(str(id)+ ",")
                for d in a.values():
                    f.write(str(d) + ",")
                id+=1 
                f.write(str(enable)+"\n")

    def write_array(self, filename, lista):
        with open(filename, "w", encoding="utf-8") as f:
            for l in lista:
                f.write(l)

    def delete(self, filename, id):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        newList = []
        for l in lines:
            arr = l.strip().split(',')
            if arr[0] == str(id):
                arr[-1] = "0"  # eliminación lógica
                l = ",".join(arr) + "\n"
            newList.append(l)
        self.write_array(filename, newList)

    def sequential_search_file(self, filename, value, param):
        index_param = -1
        with open(filename, "r") as file:
            for i, line in enumerate(file):
                arr = line.strip().split(",")
                if i == 0:
                    try:
                        index_param = arr.index(param)
                    except Exception:
                        return "No encontré la columna " + param
                elif arr[index_param] == value and arr[-1] == "1":
                    return arr
        return -1

clientes = [
    {"nombre": "Juan", "apellido": "Perez", "telefono": "3123456789"},
    {"nombre": "Maria", "apellido": "Gomez", "telefono": "3112233445"},
    {"nombre": "Carlos", "apellido": "Ramirez", "telefono": "3205566778"},
]

pedidos = [
    {"id_cliente": "1", "producto": "Laptop", "precio": "2500.00", "cantidad": "1"},
    {"id_cliente": "2", "producto": "Mouse", "precio": "20.50", "cantidad": "2"},
    {"id_cliente": "1", "producto": "Teclado", "precio": "45.00", "cantidad": "1"},
]

ventas = [
    {"id_cliente": "1", "id_pedido": "Laptop", "precio": "2500.00", "cantidad": "1"},
    {"id_cliente": "2", "id_pedido": "Mouse", "precio": "20.50", "cantidad": "2"},
    {"id_cliente": "1", "id_pedido": "Teclado", "precio": "45.00", "cantidad": "1"},
]


f = F()
f.write("clientes.csv", clientes, "id_cliente")
f.write("pedidos.csv", pedidos, "id_pedido")
f.write("ventas.csv", pedidos, "id_pedido")

def menu():
    while True:
        print("\n--- MENÚ ---")
        print("1. Registrar cliente")
        print("2. Listar clientes")
        print("3. Eliminar cliente")
        print("4. Registrar pedido")
        print("5. Listar pedidos de un cliente")
        print("6. Guardar una venta")
        print("7. Listar ventas de un cliente")
        print("8. Salir")

        op = input("Seleccione una opción: ")

        if op == "1":
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            telefono = input("Teléfono: ")
            with open("clientes.csv", "a", encoding="utf-8") as f2:
                with open("clientes.csv", "r", encoding="utf-8") as f3:
                    lines = f3.readlines()
                    id_cliente = len(lines)  # id automático
                f2.write(f"{id_cliente},{nombre},{apellido},{telefono},1\n")

        elif op == "2":
            f.read("clientes.csv")

        elif op == "3":
            idc = input("ID cliente a eliminar: ")
            f.delete("clientes.csv", idc)

        elif op == "4":
            idc = input("ID del cliente: ")
            producto = input("Producto: ")
            precio = input("Precio: ")
            cantidad = input("Cantidad: ")
            with open("pedidos.csv", "a", encoding="utf-8") as f2:
                with open("pedidos.csv", "r", encoding="utf-8") as f3:
                    lines = f3.readlines()
                    id_pedido = len(lines)
                f2.write(f"{id_pedido},{idc},{producto},{precio},{cantidad},1\n")

        elif op == "5":
            idc = input("ID cliente: ")
            with open("pedidos.csv", "r", encoding="utf-8") as f2:
                for i, linea in enumerate(f2):
                    if i == 0: continue
                    arr = linea.strip().split(",")
                    if arr[1] == idc and arr[-1] == "1":
                        print(linea.strip())

        elif op == "6":
            idc = input("ID cliente: ")
            producto = input("Producto: ")
            cantidad = input("Cantidad: ")
            precio = input("Precio unitario: ")
            with open("pedidos.csv", "a", encoding="utf-8") as f2:
                with open("pedidos.csv", "r", encoding="utf-8") as f3:
                    lines = f3.readlines()
                    id_pedido = len(lines)
                f2.write(f"{id_pedido},{idc},{producto},{precio},{cantidad},1\n")

        elif op == "7":
            nombre = input("Nombre del cliente: ")
            cliente = f.sequential_search_file("clientes.csv", nombre, "nombre")
            if cliente == -1:
                print("Cliente no encontrado")
            else:
                total = 0
                with open("pedidos.csv", "r", encoding="utf-8") as f2:
                    for i, linea in enumerate(f2):
                        if i == 0: continue
                        arr = linea.strip().split(",")
                        if arr[1] == cliente[0] and arr[-1] == "1":
                            parcial = float(arr[3]) * float(arr[4])
                            total += parcial
                            print(f"Producto: {arr[2]}, Subtotal: {parcial}")
                print("TOTAL:", total)

        elif op == "8":
            break

menu()
