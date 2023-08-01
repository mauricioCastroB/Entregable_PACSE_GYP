<template>
  <v-app>
    <div class="d-flex flex-row justify-center">
      <h1>Productos</h1>
    </div>
    <v-container>
      <v-row justify-center>
    <!--Botones Lado Izquierdo.-->
        <v-col cols="1" class="fixed-button" id="fixed-button" v-if="dialog1 === false && dialog2 === false && dialog3 === false && dialog4 === false">
          <div> <h2 style="color: black">Subida de<br>Información:</h2> </div>
          <v-btn color="#193C2E" @click="showStock" elevation="12" >Subida de Stock</v-btn>
          <v-btn color="#193C2E"  @click="showVentas" elevation="12">Subida de Ventas</v-btn>
          <div style="margin-top: 50px;"> <h2 style="color: black">Ignorados:</h2> </div>
          <v-btn color="red" @click="ignore" elevation="12">Ignorar<br>seleccionados</v-btn>
          <v-btn color="primary" @click="loadIgnoredProducts" elevation="12">Mostrar<br>ignorados</v-btn>
          <div style="margin-top: 50px;"> <h2 style="color: black">Proyecciones:</h2> </div>
          <v-btn color="#193C2E" @click="getSelectedItems" elevation="12">Proyectar<br>seleccionados</v-btn>
        </v-col>
      
    <!-- Fin Botones -->

        <v-col cols="10" style="margin-left: 150px;">
          <div class="d-flex align-center justify-center">
            <v-card elevation="11" style="margin-top: 30px;">
              <v-card-title>
                <v-text-field
                  v-model="search"
                  append-icon="mdi-magnify"
                  label="Búsqueda"
                  single-line
                  hide-details
                ></v-text-field>
              </v-card-title>
              <v-data-table
                :items-per-page="itemsPerPage"
                :headers="headers"
                :items="products"
                sort-by="Status__name"
                :sort-desc="false"
                class="elevation-1"
                @click:row="rowClick"
                @update:page="handlePageUpdate"
                :search="search"
                v-model="selectedItems"
              >
                <template v-slot:item.checkbox="{ item }">
                    <v-checkbox v-model="item.selected" @click.stop></v-checkbox>
                </template>

                <template v-slot:item.Status__name="{ item }">
                  <v-chip :color="rowBackground(item.Status_id)">
                    {{ item.Status__name }}
                  </v-chip>
                </template>
                <template v-slot:item.standby="{ item }">
                  <v-icon v-if="!item.standby" color="green">mdi-check</v-icon>
                  <v-icon v-else color="red">mdi-close</v-icon>
                </template> 
              </v-data-table>
            </v-card>
          </div>
        </v-col>
        <v-col cols="1">

        </v-col>
      </v-row>
    </v-container>
    <!--V-card emergente para subida de stock-->
    <v-dialog v-model="dialog1" max-width="900px">
      <v-card>
        <v-card-title class="headline">Productos ignorados</v-card-title>
        <v-card-text>
          <v-card-title>
            <v-text-field
              v-model="search2"
              append-icon="mdi-magnify"
              label="Búsqueda"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-data-table
            :items-per-page="ignoredItemsPerPage"
            :headers="headers"
            sort-by="Status__name"
            :items="filteredIgnoredProducts"
            item-key="id"
            :search="search2"
          >
            <template v-slot:item.checkbox="{ item }">
              <v-checkbox v-model="item.selected" @click.stop></v-checkbox>
            </template>
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
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red darken-1" text @click="dialog1 = false">Cerrar</v-btn>
          <v-btn color="green darken-1" text @click="recover">Recuperar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!--V-card emergente para subida de stock-->
    <v-dialog v-model="dialog2" max-width="700px">
      <v-card>
        <v-form @submit="uploadStock">
          <v-card-title class="headline">Subir Stock</v-card-title>
          <v-card-text>
            <v-row style="padding-left: 20px; margin-top:10px; max-height: 60px;">
              <!--v-file-input label="Seleccione el archivo de Stock" accept=".xlsx,.xls"></v-file-input-->
              <v-file-input v-model="stock_excel" label="Seleccione el archivo de Stock" accept=".xlsx,.xls" @change="handleStockFileChange"></v-file-input>
            </v-row>
            <v-row justify="center" style="margin-top:20px;">
              <v-date-picker v-model="selectedDate" label="Selecciona la fecha de ingreso de Stock"></v-date-picker>
            </v-row>
          </v-card-text>
          <span v-if="isLoading" indeterminate class="loader" style="margin-top: 5px;"></span>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red darken-1" text @click="dialog2 = false">Cerrar</v-btn>
            <v-btn color="green darken-1" text type="submit">Subir Stock</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>

    <!--V-card emergente para subida de ventas-->
    <v-dialog v-model="dialog3" max-width="700px">
      <v-card>
        <v-card-title class="headline">Subir Ventas</v-card-title>
        <v-card-text justify-center>
          <v-row style="padding-left: 20px; margin-top:10px; max-height: 60px;">
            <v-file-input v-model="ventas_excel" label="Seleccione el archivo de Ventas" accept=".xlsx,.xls" @change="handleFileChange"></v-file-input>
          </v-row>
          <span v-if="isLoading" indeterminate class="loader" style="margin-top: 5px;"></span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red darken-1" text @click="dialog3 = false">Cerrar</v-btn>
          <v-btn color="green darken-1" text @click="uploadExcel" :disabled="!ventas_excel">Subir Ventas</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog4" max-width="700px">
      <v-card>
        <v-card-title class="headline">Cargando proyecciones...</v-card-title>
        <v-card-text justify-center>
          <span v-if="isLoading" indeterminate class="loader" style="margin-top: 5px;"></span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
  </v-app>
</template>

<script>
import axios from 'axios'

export default {
  
  async asyncData() {
    const dada = await axios.get('http://127.0.0.1:8000/forecast/productos/')
    const products = dada.data.filter(product => !product.ignored && !product.deleted && product.known ).map(item => {
      return { ...item, selected: false};
    });
    return{
      itemsPerPage:10,
      isLoading: false,
      errorMSG: true,
      ventas_excel: null,
      stock_excel: null,
      selectedDate: null,
      dialog1: false,
      dialog2: false,
      dialog3: false,
      dialog4: false,
      ignoredProducts: [],
      ignoredItemsPerPage: -1,
      filterText: '',
      selectedItems: [],
      filterColumn: 'SKU',
      ignoredFilterText: '',
      ignoredFilterColumn: 'SKU',
      search: '',
      search2: '',
      //products : dada.data,
      products,
      headers: [
        {
          text: 'SKU',
          align: 'start',
          sortable: true,
          value: 'SKU',
        },
        { text: 'Descripción', value: 'description' },
        { text: 'Categoría', value: 'Category__description', maxWidth: '100'},
        { text: 'Tiempo de Restock (semanas)', value: 'restock_time' },
        { text: 'Stock Actual', value:'stock__quantity'},
        { text: 'Estado', value: 'Status__name', order:'asc'},
        { text: 'Actualizado', value: 'standby'},
        { text: 'Seleccionar', value: 'checkbox'},
      ],
      
    }
  },
  
  methods: {
    rowClick(item, row){
      const urla = 'http://localhost:3000/products/'+item.id
      window.location = urla
    },
    async uploadStock() {
      this.isLoading = true;
      const formData = new FormData();
      formData.append('excel_file', this.stock_excel);
      formData.append('selected_date', this.selectedDate); // Agregar la fecha al formulario

      await axios.post('http://localhost:8000/forecast/subida_stock/', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then(response => {
        // Manejar la respuesta del backend si es necesario
        this.isLoading = false;
        console.log(response)
        window.location.reload();
      })
      .catch(error => {
        // Manejar el error si ocurre alguno
        console.error(error);
        this.errorMSG = true;
      });
    },
    async uploadExcel() {
      this.isLoading = true;
      const formData = new FormData();
      formData.append('excel_file', this.ventas_excel);
      await axios.post('http://localhost:8000/forecast/subida_excel/', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then(response => {
        // Manejar la respuesta del backend si es necesario
        this.isLoading = false;
        window.location.reload();
      })
      .catch(error => {
        // Manejar el error si ocurre alguno
        console.error(error);
        this.errorMSG = true;
      });
    },

    async ignore() {
      for (const item of this.products) {
        if (item.selected && !item.ignored) {

          await axios.put('http://localhost:8000/forecast/productos/ignorar/' + item.id)
            .then(response => {
              // Manejar la respuesta del backend si es necesario
              console.log(response.data);

              item.ignored = true;
              item.selected = false;
            })
            .catch(error => {
              // Manejar el error si ocurre alguno
              console.error(error);
            });
        }
      }
      window.location.reload();
    },
  async loadIgnoredProducts() {
      const response = await axios.get('http://127.0.0.1:8000/forecast/productos/');
      this.ignoredProducts = response.data.filter(product => product.ignored)
        .map(product => ({ ...product, selected: false })); // Añade la propiedad selected
      this.ignoredItemsPerPage = this.ignoredProducts.length;
      this.dialog1 = true; // Muestra el diálogo
  },
  async recover() {
    for (const item of this.ignoredProducts) {
      if (item.selected) {
        await axios.put('http://localhost:8000/forecast/productos/designorar/' + item.id)
          .then(response => {
            console.log(response.data);
            item.ignored = false;
            item.selected = false;
          })
          .catch(error => {
            console.error(error);
          });
      }
    }
    this.dialog1 = false; // Cierra el diálogo
    window.location.reload();
  },
  async loadProducts() {
      // Cargar los datos de productos desde el backend
      const response = await axios.get('http://127.0.0.1:8000/forecast/productos/');
      this.products = response.data.filter(product => !product.ignored).map(item => ({ ...item, selected: false }));
  },
    
  handlePageUpdate(newPage) {
      // Actualizar el estado de la paginación y guardar en el almacenamiento local
      this.currentPage = newPage;
      localStorage.setItem('paginationPage', newPage.toString());
  },
  handleFileChange(ventas_excel) {
      console.log(ventas_excel)
      this.ventas_excel = ventas_excel;
  },
  handleStockFileChange(stock_excel) {
      console.log(stock_excel)
      this.stock_excel = stock_excel;
  },

  async showStock() {
    this.dialog2 = true;
  },
  async showVentas() {
    this.dialog3 = true;
  },
  rowBackground(id) {
    if (id === 1) return '#88dc65'
      else if (id === 2) return '#FFCE56'
      else if (id === 3) return '#FF6384'
      else return 'white'
    },
  getSelectedItems() {
    const selectedItems = this.products.filter((item) => item.selected);
    const skus = selectedItems.map(item => item.SKU); // Assuming SKU is a property of each selected item

    this.dialog4 = true
    this.isLoading = true

    axios.post('http://127.0.0.1:8000/forecast/calculo_manual_forecast/', { skus })
      .then((response) => {
        console.log('Elementos enviados con éxito', response.data);
        window.location.reload()
      })
      .catch((error) => {
        console.log('Error al enviar los elementos.', error);
        window.location.reload()
      });
  }
  
},
computed: {
  filteredProducts() {
    return this.products.filter(item => {
      const searchTerm = this.filterText.toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      const itemValue = item[this.filterColumn].toString().toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      return itemValue.includes(searchTerm);
    });
  },
  filteredIgnoredProducts() {
    return this.ignoredProducts.filter(item => {
      const searchTerm = this.ignoredFilterText.toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      const itemValue = item[this.ignoredFilterColumn].toString().toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      return itemValue.includes(searchTerm);
    });
  },
  noMatches() {
    return this.filteredProducts.length === 0;
  },
  noIgnoredMatches() {
    return this.filteredIgnoredProducts.length === 0;
  },
  updateProducts(){
    return 1
  }
  
}
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