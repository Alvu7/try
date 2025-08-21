import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class Banco {

    public void crearArchivo(String filename) {
        Path out = Paths.get(filename);
        try (BufferedWriter bw = Files.newBufferedWriter(out,
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING)) {

            bw.write("12345,Jose,50.43\n");
            bw.write("54321,Dario,43.12\n");
            bw.write("67890,Ana,70.10\n");
            bw.write("11111,Pedro,30.00\n");

        } catch (IOException e) {
            System.err.println("Error al crear archivo: " + e.getMessage());
        }
    }
    public void consultarSaldo(String filename, String nombreBuscado) {
        Path ruta = Paths.get(filename);
        try (BufferedReader br = Files.newBufferedReader(ruta, StandardCharsets.UTF_8)) {
            String linea;
            boolean encontrado = false;

            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(",");
                String nombre = partes[1];
                double saldo = Double.parseDouble(partes[2]);

                if (nombre.equalsIgnoreCase(nombreBuscado)) {
                    System.out.println("El saldo de " + nombre + " es: " + saldo);
                    encontrado = true;
                }
            }

            if (!encontrado) {
                System.out.println("Cliente no encontrado.");
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public void contarMayores50(String filename) {
        Path ruta = Paths.get(filename);
        int contador = 0;

        try (BufferedReader br = Files.newBufferedReader(ruta, StandardCharsets.UTF_8)) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(",");
                double saldo = Double.parseDouble(partes[2]);
                if (saldo > 50) {
                    contador++;
                }
            }
            System.out.println("Clientes con saldo mayor a 50: " + contador);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public void ordenarPorSaldo(String filename) {
        Path ruta = Paths.get(filename);
        List<String[]> clientes = new ArrayList<>();

        try (BufferedReader br = Files.newBufferedReader(ruta, StandardCharsets.UTF_8)) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(",");
                clientes.add(partes);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        clientes.sort((a, b) -> Double.compare(Double.parseDouble(a[2]), Double.parseDouble(b[2])));

        System.out.println("Clientes ordenados por saldo:");
        for (String[] cliente : clientes) {
            System.out.println(cliente[1] + " -> " + cliente[2]);
        }
    }
    public static void main(String[] args) {
        Banco banco = new Banco();
        String archivo = "datos.txt";

        banco.crearArchivo(archivo);

        Scanner sc = new Scanner(System.in);
        int opcion;

        do {
            System.out.println("\n--- MENÚ BANCO ---");
            System.out.println("1. Consultar saldo de cliente");
            System.out.println("2. Contar clientes con saldo > 50");
            System.out.println("3. Mostrar clientes ordenados por saldo");
            System.out.println("0. Salir");
            System.out.print("Elige una opción: ");
            opcion = sc.nextInt();
            sc.nextLine(); // limpiar buffer

            switch (opcion) {
                case 1:
                    System.out.print("Ingrese nombre del cliente: ");
                    String nombre = sc.nextLine();
                    banco.consultarSaldo(archivo, nombre);
                    break;
                case 2:
                    banco.contarMayores50(archivo);
                    break;
                case 3:
                    banco.ordenarPorSaldo(archivo);
                    break;
                case 0:
                    System.out.println("Saliendo...");
                    break;
                default:
                    System.out.println("Opción inválida");
            }
        } while (opcion != 0);

        sc.close();
    }
}


