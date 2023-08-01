<template>
    <v-app>
        <!--Titulo y subtitulo de la ventana-->
        <div class="d-flex flex-row justify-center">
            <h1>Categorías</h1>
        </div>
        <div class ="d-flex flex-row justify-center">
            <p>Editar o Crear Categorías</p>
        </div>
        <!--Container con las V-cards de los productos nuevos/desconocidos-->
        <v-container>
            <v-row>
                <!-- Botones al costado -->
                <v-col
                cols="9"
                md="2">
                    <div class="fixed-button" id="fixed-button" style="margin-top: 40px;" >
                        <div style="margin-top: 50px;"> <h2 style="color: black">Acciones:</h2> </div>
                        <v-btn color="#193C2E" @click="dialog_create=true" elevation="12" >Crear Categoría</v-btn>
                    </div>
                </v-col>
                <v-col
                md="8" >
                    <v-row v-for = "row in nrows" :key = "row">
                        <v-col v-for = "col in 3" :key = "col">
                            <CardCategory
                            :id="categories[(row -1)*3 + col].id"
                            :description="categories[(row -1)*3 + col].description"
                            v-if = "(row -1)*3 + col < categories.length && categories[(row -1)*3 + col].id != 1"
                            />
                        </v-col>
                    </v-row>
                </v-col>
            </v-row>
        </v-container>

        

        <!-- Dialogo Crear Categoría -->
        <v-dialog v-model="dialog_create" max-width="700px">
            <v-card>
                <v-card-title class="headline">Crear Categoría</v-card-title>
                <v-card-text justify-center>
                    <v-row style="padding-left: 20px; margin-top:10px; max-height: 60px;">
                        <v-text-field v-model="description" label="Escriba el nombre de la nueva categoría"></v-text-field>
                    </v-row>
                    <span v-if="isLoading" indeterminate class="loader" style="margin-top: 5px;"></span>
                </v-card-text>
                <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="red darken-1" text @click="dialog_create = false">Cerrar</v-btn>
                <v-btn color="green darken-1" text @click="createCategory">Crear</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
  </v-app>
</template>

<script>
import axios from 'axios';

export default{
    async asyncData() {
        const data = await axios.get("http://127.0.0.1:8000/forecast/get_all_categories");
        const categories = data.data;
        return {
            categories,
            dialog_create: false,
            isLoading: false,
            description: '',
        };
    },
    methods: {
        async createCategory(){
            await axios.post("http://127.0.0.1:8000/forecast/create_category/", this.description);
            this.isLoading=true
            window.location.reload()
        }
    },
    computed: {
        nrows() {
            let nrows = Math.floor((this.categories.length - 1) / 3) + 1;
            return Math.floor((this.categories.length - 1) / 3) + 1;
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