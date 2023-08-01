<template>
    <v-app>
        <div class="container">
            <div class="d-flex flex-row justify-center">
                <h1>Configuración</h1>
                </div>
                <div class ="d-flex flex-row justify-center">
                <p>Seleccione los datos que desea configurar</p>
            </div>
            <v-row>
                <v-col cols="4">
                    <v-card class="vcard">
                        <v-card-title>Editar Productos</v-card-title>
                        <v-card-text>
                            Editar y eliminar los productos
                        </v-card-text>
                        <v-card-text>
                            <v-btn href="/edit/products" color="primary">
                                Ir
                            </v-btn>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="4">
                    <v-card class="vcard">
                        <v-card-title>Editar Categorías</v-card-title>
                        <v-card-text>
                            Crear, editar y eliminar las categorías de los productos
                        </v-card-text>
                        <v-card-text>
                            <v-btn href="/edit/categories" color="primary">
                                Ir
                            </v-btn>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="4">
                    <v-card class="vcard">
                        <v-card-title>Eliminar datos</v-card-title>
                        <v-card-text>
                            Formatear los datos a iniciales.
                        </v-card-text>
                        <v-card-text>
                            <v-btn href="/exit" color="primary">
                                Ir
                            </v-btn>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </div>
    </v-app>
</template>

<style>
.vcard {
    height: 200px;
}
</style>