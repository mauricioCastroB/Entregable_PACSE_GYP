// Función para contar los elementos que cumplen la condición
export function contarElementos(diccionario, condicion) {
  var contador = 0;

  // Recorrer el diccionario
  for (var i=0; i < diccionario.length; i++) {
    // Verificar si la propiedad id_status cumple la condición
    if (
      diccionario[i].Status_id === condicion
    ) {
      contador++;
    }
  }

  return contador;
}