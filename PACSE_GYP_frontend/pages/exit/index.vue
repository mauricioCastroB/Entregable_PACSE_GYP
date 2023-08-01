<template>
  <div class="container">
    <div class="d-flex flex-row justify-center">
      <h1>Eliminar toda la información de las ventas</h1>
    </div>

    <div class="d-flex align-center justify-center">
      <v-card elevation="11" style="margin-top: 30px;">
        <v-card-text>
          <v-btn color="primary" variant="tonal" @click="btn_drop">Borrar información</v-btn>
        </v-card-text>
      </v-card>

    </div>


    <v-row justify="center">
      <v-dialog v-model="dialog2" width="auto">

        <v-card>
          <v-card-title class="text-h5">
            ¿Seguro que desea eliminar toda la información?
          </v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn class="red--text" color="green-darken-1" variant="tonal " @click="dialog2 = false">
              Cancelar
            </v-btn>
            <v-btn color="green--text" variant="tonal" @click="drop">
              Aceptar
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>


  </div>
</template>
  
<script>

import axios from 'axios';
export default {
  asyncData() {
    return {
      dialog2: false,
    }

  },
  methods: {

    async drop() {
      this.dialog2 = false;
      await axios.get('http://localhost:8000/forecast/drop/');
      return this.$router.push('/products');
    },
    btn_drop() {
      this.dialog2 = true;
    }
  }
}
</script>
  