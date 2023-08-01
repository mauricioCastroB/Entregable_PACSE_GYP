<script>
import { Doughnut, mixins } from 'vue-chartjs';
const { reactiveProp } = mixins;

export default {
  
  extends: Doughnut,
  mixins: [reactiveProp],
  props: ['chartData', 'options_Donut'],
  mounted() {
    this.renderChart(this.chartData, this.options);
  }
};
</script>