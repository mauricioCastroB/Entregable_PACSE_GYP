<template>
    <v-card>
        <!--Titulo de la v-card con el nombre del producto-->
        <v-card-title class="headline">Categoría: {{ id }}</v-card-title>
        
        <!--Conjunto de textfield con la información-->

        <v-row justify="center" class = "comboSize">
            <v-text-field v-model = "descriptionValue" label="Nombre"></v-text-field>
        </v-row>

        <!--Botones para guardar o eliminar-->
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn v-if="id != 1" color="green darken-1" text @click ="revealSave = true"> Guardar </v-btn>
            <v-btn v-else color="green darken-1" text disabled> Guardar </v-btn>
        </v-card-actions>

        <!--V-Card emergente para guardar la información del producto-->
        <v-expand-transition>
            <v-card v-if="revealSave" class="v-card--reveal" style="height: 100%;">
                <v-card-text>
                    <p class="text--primary text-center">
                        <b>¿Deseas guardar los datos de esta categoría?</b>
                    </p>
                    <div class="text-center">
                        Nombre: <b>{{ descriptionValue }}</b>
                    </div>
                </v-card-text>
                <v-card-actions>
                    <v-row justify="center">
                        <v-col cols="auto">
                            <v-btn text color="red darken-1" @click="revealSave = false" small>Cancelar</v-btn>
                        </v-col>
                        <v-col cols="auto">
                            <v-btn text color ="green darken-1" @click="saveDataCategory" small>Aceptar</v-btn>
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
    props: ['id','description'],
    data: function() {
        return{
            //Retorno información a utilizar para la v-card del producto
            revealDelete: false,
            revealSave: false,
            descriptionValue: this.description,
            idValue: this.id,
        }
    },
    methods: {
        //Función para guardar la información del producto
        async saveDataCategory(){
            //Axios para guardar los valores
            const categoryData ={
                'description': this.descriptionValue,
            };
            await axios.patch('http://127.0.0.1:8000/forecast/update_category/' + this.idValue, categoryData);

            window.location.reload();
            
        },
    },
}
</script>