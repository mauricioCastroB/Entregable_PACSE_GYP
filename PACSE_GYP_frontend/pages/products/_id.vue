<template>
  <section>
    <div>
      <div class="d-flex flex-row justify-center">
        <h1>Proyección</h1>
      </div>
      <v-btn
        label="Volver" 
        @click="retroceder()" 
      >Atras</v-btn>
      <div class="chart">
        <LineChart :data="lineChartData" :options="lineChartOptions" :height="200" />
      </div>
    </div>
  </section>
</template>

<script>
import LineChart from "~/components/LineChart.vue";
import axios from 'axios';

export default {
  components: { LineChart },
  async asyncData({params }) {

    const url = 'http://127.0.0.1:8000/forecast/predicciones/' + params.id
    const dada = await axios.get(url)


    const url2 = 'http://127.0.0.1:8000/forecast/productos/' + params.id
    const product = await axios.get(url2)

    const dic = dada.data
    const fechas_sales = dic.sales_dates
    const fechas_forecast = dic.forecast_dates
    var fechas = fechas_sales.concat(fechas_forecast)
    fechas = fechas.map(str => str.substring(0, 10));


    const sales = dic.sales_units
    const forecast = dic.forecast_units

    const ventas = sales.concat(forecast)

    var top = Math.max(...ventas)+5
    
    var span = Array.from({ length: sales.length }, () => null)
    
    return {
      
      lineChartData: {
        labels: fechas,
        datasets: [
          {
            label: "Ventas",
            data: [...sales, forecast[0]],
            backgroundColor: "rgba(20, 255, 0, 0.3)",
            borderColor: "rgba(100, 255, 0, 1)",
            borderWidth: 2,
          },
          {
            label: "Proyección",
            data: [...span ,...forecast],
            borderColor: "rgba(0,255,255,1)",
            backgroundColor: "rgba(0,255,255,0.3)",
            borderWidth: 2
          }
        ],
      },
      lineChartOptions: {
        responsive: true,
        legend: {
          display: false,
        },
        title: {
          display: true,
          text: product.data.description,
          fontSize: 24,
          fontColor: "#6b7280",
        },
        tooltips: {
          backgroundColor: "#17BF62",
        },
        scales: {
          xAxes: [
            {
              gridLines: {
                display: true,
              },
            },
          ],
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
                max: top,
                min: 0,
                stepSize: 5,
              },
              gridLines: {
                display: true,
              },
            },
          ],
        },
      },
    };
  },
  methods:{
    retroceder(){
      this.$router.push('/products/') 
    }
  }
};
</script>

