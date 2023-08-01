<template>
    <v-card>
        <!--Titulo de la v-card con el nombre del producto-->
        <v-card-title class="headline">Producto: {{ sku }}</v-card-title>
        
        <!--Conjunto de textfield con la información-->

        <v-row justify="center" class = "comboSize">
            <v-text-field v-model = "descriptionValue" label="Nombre"></v-text-field><br>
        </v-row>
        <v-row style="margin-top: 10px;" class="comboSize">
            <v-combobox
            v-model = "categoryValue"
            label = "Categoría"
            outlined
            :items = "category_list">
            </v-combobox>
        </v-row>
        <v-row justify="center" class = "comboSize">
            <v-text-field v-model = "stock_dateValue" label="Tiempo de Restock"></v-text-field><br>
        </v-row>

        <!--Botones para guardar o eliminar-->
        <v-card-actions>
            <v-btn color="red darken-1" text @click="revealDelete = true">Eliminar</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" text @click ="revealSave = true"> Guardar </v-btn>
        </v-card-actions>

        <!--V-Card emergente para borrar el producto-->
        <v-expand-transition>
            <v-card v-if="revealDelete" class="v-card--reveal" style="height: 100%;">
                <v-card-text>
                    <p class="text--primary text-center">
                        <b>¿Está seguro que desea eliminar este producto?</b>
                    </p>
                    <div class="text-center">
                        Nombre: <b>{{ descriptionValue }}</b>
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-row align="end" justify="center">
                        <v-col cols="auto">
                            <v-btn text color="red darken-1" @click="revealDelete = false" small>Cancelar</v-btn>
                        </v-col>
                        <v-col cols="auto">
                            <v-btn text color ="green darken-1" @click="deleteProduct" small>Aceptar</v-btn>
                        </v-col>
                    </v-row>
                </v-card-actions>
            </v-card>
        </v-expand-transition>

        <!--V-Card emergente para guardar la información del producto-->
        <v-expand-transition>
            <v-card v-if="revealSave" class="v-card--reveal" style="height: 100%;">
                <v-card-text>
                    <p class="text-center">
                        <b>¿Desea guardar los datos de este producto?</b>
                    </p>
                    <div class="text-center">
                        Nombre: <b>{{ descriptionValue }}</b><br>
                        Clase: <b>{{ categoryValue }}</b>
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-row align="end" justify="center">
                        <v-col cols="auto">
                            <v-btn text color="red darken-1" @click="revealSave = false" small>Cancelar</v-btn>
                        </v-col>
                        <v-col cols="auto">
                            <v-btn text color ="green darken-1" @click="saveDataProduct" small>Aceptar</v-btn>
                        </v-col>
                    </v-row>
                </v-card-actions>
            </v-card>
        </v-expand-transition>
    </v-card>

</template>

<style>
.comboSize{
    margin-right: 15px;
    margin-left: 15px;
}
.v-card--reveal {
  bottom: 0;
  opacity: 1 !important;
  position: absolute;
  width: 100%;
}
</style>

<script>
import axios from 'axios';

export default{
    //Datos de entrada para rellenar la informacion de la v-card
    props: ['id','description','category','sku','category_list','stock_dateValue'],
    data: function() {
        return{
            //Retorno información a utilizar para la v-card del producto
            revealDelete: false,
            revealSave: false,
            descriptionValue: this.description,
            idValue: this.id,
            categoryValue: this.category,
        }
    },
    methods: {
        //Función para guardar la información del producto
        async saveDataProduct(){
            //Axios para guardar los valores
            const productData ={
                'description': this.descriptionValue,
                'category': this.categoryValue,
                'restock_time': this.stock_dateValue,
            };
            await axios.patch('http://127.0.0.1:8000/forecast/update_product/' + this.idValue, productData);

            window.location.reload();
            
        },
        //Función para eliminar el producto
        async deleteProduct(){
            //Axios para borrar el producto
            await axios.patch('http://127.0.0.1:8000/forecast/productos_known/eliminar/'+ this.idValue);
            window.location.reload();
        }
    },
}
</script>