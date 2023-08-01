<template>
  <v-app>
    <!--Titulo y subtitulo de la ventana-->
    <div class="d-flex flex-row justify-center">
      <h1>Productos Nuevos/Desconocidos</h1>
    </div>
    <div class ="d-flex flex-row justify-center">
      <p>Verifique los datos de los siguientes productos</p>
    </div>
    <!--Container con las V-cards de los productos nuevos/desconocidos-->
    <v-container>
      <v-row v-for = "row in nrows" :key = "row">
        <v-col v-for = "col in 2" :key = "col">
          <CardUnknown
          :sku = "productsUnkown[(row -1)*2 + col-1].SKU"
          :skuList = "SKUs"
          :description = "productsUnkown[(row -1)*2 + col-1].description"
          :descriptionList = "descriptions"
          :category = "productsUnkown[(row -1)*2 + col-1].Category__description"
          :categoryList = "categorys"
          :id = "productsUnkown[(row -1)*2 + col-1].id"
          v-if = "(row -1)*2 + col-1 < productsUnkown.length"/>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import axios from 'axios'
export default {
    async asyncData() {
        //Obtención de los productos nuevos/desconocidos en la base de datos
        const dada = await axios.get("http://127.0.0.1:8000/forecast/productos/");
        const products_not_deleted = dada.data.filter(product => !product.deleted)
        const productsUnkown = dada.data.filter(product => !product.known && !product.deleted);

        //Listado de información para los combobox
        const SKUs = products_not_deleted.map(product => product.SKU)
        const descriptions = products_not_deleted.map(product => product.description)
        const categorys = products_not_deleted.map(product => product.Category__description)
        return {
            productsUnkown,
            SKUs,
            descriptions,
            categorys,
        };
    },
    methods: {},
    computed: {
      nrows(){
        let nrows = Math.floor((this.productsUnkown.length -1)/2) +1
        return Math.floor((this.productsUnkown.length -1)/2) +1;
      }
    }
}

</script>