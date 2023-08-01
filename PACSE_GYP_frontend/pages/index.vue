<template>
    <v-app>
        <div class="d-flex flex-row justify-center" style="margin-bottom: 10px;"><h1>Dashboard</h1></div>
        <div class="d-flex flex-row justify-center">
            <div class="d-flex flex-column align-center justify-top">
                
                <v-img src="Logo 3Angeli Verde.jpg" max-width="300"></v-img>
                <v-card class="standard-width" elevation="11">
                    <v-card-title>
                        Última carga de ventas:
                    </v-card-title>
                    <v-card-text>
                        <h1 v-if="this.veri_2_weeks" style="color: red;">{{ this.sales_date }}</h1>
                        <h1 v-else>{{ this.sales_date }}</h1>
                        <p v-if="this.veri_2_weeks"> Es necesario actualizar las Ventas </p>
                    </v-card-text>
                    <v-card-title style="margin-right: 20; " >
                        Última carga de Stock:
                    </v-card-title>
                    <v-card-text>
                        <h1 style="color: red;">{{ this.stock_date }}</h1>
                        <p v-if="!this.veri_2_weeks"> No se ha actualizado el stock en {{ this.warn_stock.substring(0, 2) }} días </p>
                        <p v-else> No hay información </p>
                    </v-card-text>
                </v-card>
            </div>
           
            <v-card style="margin-right: 20px; margin-left: 20px;" elevation="11" class="standard-width">
                <v-card-title>
                    Productos por Estado
                </v-card-title>
                <my-doughnut-chart
                :chart-data="chartData"
                :options="options_Donut"
                style="margin-top: 30px;"
                >
                </my-doughnut-chart>
            </v-card>
            <div class="d-flex flex-column">
                <v-card elevation="11" style="margin-bottom: 50px;" class="standard-width">
                    <v-card-title>
                        Productos con Estimación<br>actualizada:
                    </v-card-title>
                    <v-card-text>
                        <h1 style="color: green;">{{ num_actualizado }}</h1>
                    </v-card-text>
                    <v-card-title>
                        Productos Sin Estimación<br>actualizada:
                    </v-card-title>
                    <v-card-text>
                        <h1 style="color: grey;">{{ num_no_actualizado }}</h1>
                    </v-card-text>
                    <v-card-text justify-end>
                        <v-btn outlined @click="updateUptoDate"> Actualizar </v-btn>
                    </v-card-text>
                </v-card>
                <v-card max-height="250px" elevation="11">
                    <v-card-title>
                        Porcentaje de productos que<br>
                        exceden 8 meses de venta:
                    </v-card-title>
                    <v-card-text>
                        <h1 v-if="this.percent > 0">{{this.percent.toFixed(2)}}%</h1>
                        <h1 v-else>0%</h1>
                    </v-card-text>
                </v-card>
            </div>
            
        </div>
        <div class="d-flex flex-row justify-center" style="margin-top: 40px;">
            <v-card style="margin-right: 20px;" elevation="11">
                <v-card-title>
                    Productos que requieren atención
                </v-card-title>
                <v-data-table
                :items-per-page=10
                :headers="headers"
                :items="products_danger"
                sort-by="Status__name"
                :sort-desc="false"
                class="elevation-1"
                >
                    <template v-slot:item.Status__name="{ item }">
                        <v-chip :color="rowBackground(item.Status_id)">
                            {{ item.Status__name }}
                        </v-chip>
                    </template>
                    <template v-slot:item.standby="{ item }">
                        <v-icon v-if="!item.standby">mdi-check</v-icon>
                        <v-icon v-else>mdi-close</v-icon>
                    </template>
                </v-data-table>
            </v-card>
            
        </div>
        <!-- Dialogo Crear Product -->
        <v-dialog v-model="dialog1" max-width="700px">
            <v-card>
                <v-card-title class="headline">Verificando Actualización de los productos</v-card-title>
                <v-card-text justify-center>
                    <span v-if="isLoading" indeterminate class="loader" style="margin-top: 5px;"></span>
                </v-card-text>
            </v-card>
        </v-dialog>
    </v-app>
</template>

<script>
import axios from 'axios';
import { contarElementos } from '~/assets/js/contador_status.js';
import MyDoughnutChart from '@/components/MyDoughnutChart.vue';

export default{
    namePage: 'IndexPage',
    
    async asyncData(){
        const dada = await axios.get('http://127.0.0.1:8000/forecast/productos/')
        const last_sale = await axios.get('http://127.0.0.1:8000/forecast/sale/last_sales/')
        const last_stock = await axios.get('http://127.0.0.1:8000/forecast/sale/last_stock/')
        const products = dada.data.filter(product => !product.ignored && !product.deleted && product.known).map(item => {
            return { ...item, selected: false };
        });

        const products_danger = products.filter(product => product.Status_id === 3)

        var percent = (products_danger.length / products.length) * 100

        var sales_date = last_sale.data.last_date
        var veri_2_weeks = last_sale.data.actualizar

        var stock_date = last_stock.data.last_date
        var warn_stock = last_stock.data.dif_date

        return{
            products_danger,
            num_actualizado: 0,
            num_no_actualizado: 0,
            stock_date,
            warn_stock,
            sales_date,
            veri_2_weeks,
            percent,
            dialog1:false,
            isLoading:false,
            products,
            // Datos para el gráfico de Dona
            chartData: {
                labels: ['Peligro', 'Advertencia', 'Seguro','Sin Estado'],
                datasets: [
                {
                    label: 'Datos del gráfico',
                    backgroundColor: ['#FF6384', '#FFCE56', '#88dc65'],
                    data: [contarElementos(products,3), contarElementos(products,2), contarElementos(products,1),contarElementos(products,4)]
                }
                ]
            },
            options_Donut: {
                responsive: true,
                maintainAspectRatio: false
            },
            headers: [
                {
                text: 'SKU',
                align: 'start',
                sortable: true,
                value: 'SKU',
                },
                { text: 'Descripción', value: 'description' },
                { text: 'Categoría', value: 'Category__description' },
                { text: 'Tiempo de Restock (semanas)', value: 'restock_time' },
                { text: 'Stock Actual', value:'stock__quantity'},
                { text: 'Actualizado', value:'standby'},
                { text: 'Estado', value: 'Status__name', order:'asc'},
            ],
        };
    },
    methods: {
        contarElementos(diccionario, condicion){
            var contador = 0;

            // Recorrer el diccionario
            for (var clave in diccionario) {
                // Verificar si el valor cumple la condición
                if (diccionario.hasOwnProperty(clave) && diccionario[clave].id_status === condicion) {
                contador++;
                }
            }

            return contador;
        },
        rowBackground(id) {
            if (id === 1) return '#88dc65'
            else if (id === 2) return '#FFCE56'
            else if (id === 3) return '#FF6384'
            else return 'white'
        },
        // Función para contar la ocurrencia de la variable en la lista
        async contarVariable(lista, variable) {
            console.log(lista)
            let contador = 0;
            for (var item of lista) {
                console.log(item)
                if (item.standby === variable) {
                contador++;
                }
            }
            return contador;
        },
        
        async updateUptoDate() {
            this.dialog1=true
            this.isLoading=true
            await axios.patch('http://127.0.0.1:8000/forecast/update_standby')
            window.location.reload()
        },
    },
    components: {
        MyDoughnutChart
    },
    mounted() {
        this.contarVariable(this.products, false).then((resultado) => {
            this.num_actualizado = resultado;})
        this.contarVariable(this.products, true).then((resultado) => {
            this.num_no_actualizado = resultado;})
    }
}

</script>

<style>

.standard-width {
    width: 300px;
}


</style>