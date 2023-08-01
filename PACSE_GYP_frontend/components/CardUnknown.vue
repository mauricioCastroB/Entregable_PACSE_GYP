<template>
    <v-card>
        <!--Titulo de la v-card con el nombre del producto-->
        <v-card-title class="headline">Producto: {{description}}</v-card-title>

        <!--Conjunto de combobox con la información-->
        <v-row justify="center" class = "comboSize">
            <v-combobox
            v-model = "skuValue"
            label = "SKU"
            outlined
            :items = "skuList"
            @change="updateComboboxSKU">
            </v-combobox>
        </v-row>

        <v-row justify="center" class = "comboSize">
            <v-combobox
            class = "comboSize"
            v-model = "descriptionValue"
            label = "Descripción"
            outlined
            :items = "descriptionList"
            @change="updateComboboxDescription">
            </v-combobox>
        </v-row>

        <v-row justify="center" class = "comboSize">
            <v-combobox
            class = "comboSize"
            v-model = "categoryValue"
            label = "Categoría"
            outlined
            :items = "categoryList">
            </v-combobox>
        </v-row>

        <!--Botones para guardar o eliminar-->
        <v-card-actions>
            <v-btn color="red darken-1" text @click="revealDelete = true">Eliminar</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" text @click ="revealSave = true"> Guardar </v-btn>
        </v-card-actions>

        <!--V-Card emergente para borrar el producto-->
        <v-expand-transition>
            <v-card v-if="revealDelete" :loading = "loading_delete" class="v-card--reveal" style="height: 100%;">
                <v-card-text>
                    <p class="text-h3 text--primary text-center">
                        ¿Estas seguro que deseas eliminar este producto?
                    </p>
                    <div class="text-center">
                        SKU: <b>{{ skuValue }}</b> <br>
                        Descripción: <b>{{ descriptionValue }}</b><br>
                        Categoría: <b>{{ categoryValue }}</b>
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-row align="end" justify="center">
                        <v-col cols="auto">
                            <v-btn text :disabled = "disable_buttons" color="red darken-1" @click="revealDelete = false" x-large>Cancelar</v-btn>
                        </v-col>
                        <v-col cols="auto">
                            <v-btn text :disabled = "disable_buttons" color ="green darken-1" @click="deleteProduct" x-large>Aceptar</v-btn>
                        </v-col>
                    </v-row>
                </v-card-actions>
            </v-card>
        </v-expand-transition>

        <!--V-Card emergente para guardar la información del producto-->
        <v-expand-transition>
            <v-card v-if="revealSave" :loading = "loading_modificate" class="v-card--reveal" style="height: 100%;">
                <v-card-text>
                    <p class="text-h3 text--primary text-center">
                        ¿Deseas guardar los datos de este producto?
                    </p>
                    <div class="text-center">
                        SKU: <b>{{ skuValue }}</b> <br>
                        Descripción: <b>{{ descriptionValue }}</b><br>
                        Categoría: <b>{{ categoryValue }}</b>
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-row align="end" justify="center">
                        <v-col cols="auto">
                            <v-btn text :disabled = "disable_buttons" color="red darken-1" @click="revealSave = false" x-large>Cancelar</v-btn>
                        </v-col>
                        <v-col cols="auto">
                            <v-btn text :disabled = "disable_buttons" color ="green darken-1" @click="saveDataProduct" x-large>Aceptar</v-btn>
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
    props: ['id','sku','description','category','skuList','descriptionList','categoryList'],
    data: function() {
        return{
            //Retorno información a utilizar para la v-card del producto
            revealDelete: false,
            revealSave: false,
            skuValue: this.sku,
            descriptionValue: this.description,
            categoryValue: this.category,
            idValue: this.id,
            loading_modificate: false,
            loading_delete: false,
            disable_card: false
        }
    },
    methods: {
        async updateComboboxSKU(){
            var positionSKU = this.skuList.indexOf(this.skuValue);
            this.descriptionValue = this.descriptionList[positionSKU];
        },
        async updateComboboxDescription(){
            var positionDescription = this.descriptionList.indexOf(this.descriptionValue);
            this.skuValue = this.skuList[positionDescription];
        },
        //Función para guardar la información del producto
        async saveDataProduct(){

            //Se desactiva la vcard y se muestra el barra de carga
            this.disable_buttons = true;
            this.loading_modificate = true;
            //Axios para guardar los valores
            const productData ={
                'SKU' : this.skuValue,
                'description': this.descriptionValue,
                'category': this.categoryValue
            };
            await axios.patch('http://127.0.0.1:8000/forecast/productos_known/modificar/' + this.idValue, productData);

            this.loading_modificate = false;
            this.disable_buttons = false;
            window.location.reload();
            
        },

        //Función para eliminar el producto
        async deleteProduct(){
            //Se desactiva la vcard y se muestra el barra de carga
            this.disable_buttons = true;
            this.loading_delete = true;
            //Axios para borrar el producto
            await axios.patch('http://127.0.0.1:8000/forecast/productos_known/eliminar/'+ this.idValue);
            this.loading_delete = false;
            this.disable_buttons = false;
            window.location.reload();
        }
    },
}
</script>