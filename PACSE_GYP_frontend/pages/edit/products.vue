<template>
    <v-app>
        <!--Titulo y subtitulo de la ventana-->
        <div class="d-flex flex-row justify-center">
            <h1>Producto</h1>
        </div>
        <div class ="d-flex flex-row justify-center">
            <p>Editar o eliminar Productos</p>
        </div>
        <!--Container con las V-cards de los productos nuevos/desconocidos-->
        <v-container>
            <v-row>
                <v-col>
                    <v-row v-for = "row in nrows" :key = "row">
                        <v-col v-for = "col in 3" :key = "col">
                            <CardProduct
                            :sku = "products[(row -1)*3 + col-1].SKU"
                            :id = "products[(row -1)*3 + col-1].id"
                            :description = "products[(row -1)*3 + col-1].description"
                            :category = "products[(row -1)*3 + col-1].Category__description"
                            :stock_dateValue = "products[(row -1)*3 + col-1].restock_time"
                            :category_list = "categories"
                            v-if = "(row -1)*3 + col-1 < products.length"
                            />
                        </v-col>
                    </v-row>
                </v-col>
            </v-row>
        </v-container>

        

        <!-- Dialogo Crear Product -->
        <v-dialog v-model="dialog_create" max-width="700px">
            <v-card>
                <v-card-title class="headline">Crear Producto</v-card-title>
                <v-card-text justify-center>
                    <v-row style="padding-left: 20px; margin-top:10px; max-height: 60px;">
                        <v-text-field v-model="sku_name" label="Escriba el SKU del nuevo producto"></v-text-field>
                    </v-row>
                    <v-row style="padding-left: 20px; margin-top:10px; max-height: 60px;">
                        <v-text-field v-model="product_name" label="Escriba el nombre del nuevo producto"></v-text-field>
                    </v-row>
                    <v-row style="margin-top: 10px;">
                        <v-combobox
                        v-model = "categoryValue"
                        label = "Categoría"
                        outlined
                        :items = "categories">
                        </v-combobox>
                    </v-row>
                    <span v-if="isLoading" indeterminate class="loader" style="margin-top: 5px;"></span>
                </v-card-text>
                <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="red darken-1" text @click="dialog_create = false">Cerrar</v-btn>
                <v-btn color="green darken-1" text @click="createProduct">Crear</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
  </v-app>
</template>

<script>
import axios from 'axios';

export default{
    async asyncData() {
        const dada = await axios.get("http://127.0.0.1:8000/forecast/productos/");
        const products = dada.data.filter(product => !product.deleted);
        const categories = dada.data.map(product => product.Category__description)
        return {
            products,
            categories,
            dialog_create: false,
            isLoading: false,
            sku_name: '',
            product_name: '',
            categoryValue: '',
        };
    },
    methods: {
        createProduct(){
            
            this.isLoading=true
        }
    },
    computed: {
        nrows() {
            let nrows = Math.floor((this.products.length - 1) / 3) + 1;
            return Math.floor((this.products.length - 1) / 3) + 1;
        }
    },
}

</script>

<style>
.fixed-button {
  position: fixed;
  left: 20px;
  z-index: 9999;
  width: 180px;
}

#fixed-button > * {
  margin-top: 20px;
  width: 180px;
  color: white;
}
</style>