<template>
    <v-app>
      <v-app-bar
        :clipped-left="clipped"
        fixed
        app
        color="#193C2E"
        dark
        fade-img-on-scroll
      >
      <router-link to="/">
        <v-img
          max-width="155"
          src="/logo.jpg"
          href="/"
          contain
        ></v-img>
      </router-link>
        <v-spacer />
        <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      </v-app-bar>
      <v-navigation-drawer
        v-model="drawer"
        :mini-variant="miniVariant"
        :clipped="clipped"
        fixed
        app
        temporary
        right
        style="background-color: #193C2E;"
        
      >
      <div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
        <v-list dark >
          <v-list-item
            v-for="(item, i) in items"
            :key="i"
            :to="item.to"
            router
            exact
          >
            <v-list-item-action>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        
        <v-divider></v-divider>
        <v-list dark >
        <!-- Boton para cerrar ejecutable -->
        <v-list-item @click="salir">
          <v-list-item-action>
            <v-icon>mdi-logout</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Salir</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

      </v-list>
    </div>
      </v-navigation-drawer>
      <v-dialog transition="dialog-bottom-transition" width="auto" v-model="dialog1">
        <v-card>
          <v-card-text>
            <div class="text-h2 pa-12">Aplicación cerrada</div>
          </v-card-text>
        </v-card>
      </v-dialog>
      <v-main>
        <v-container>
          <Nuxt />
        </v-container>
      </v-main>
      <v-footer
        :absolute="!fixed"
        app
        style="background-color: #193C2E;"
      >
        <v-card
          tile
          flat
          width="100%"
          color="#193C2E"
          dark
          height="75px"
          class="d-flex align-center justify-center"
          >
          <div class="d-flex flex-row justify-center">
            <span>&copy; {{ new Date().getFullYear() }}</span>
          </div>

        </v-card>
      </v-footer>
    </v-app>
  </template>
  
  <script>
  import axios from 'axios';
  export default {
    name: 'DefaultLayout',
    data () {
      return {
        dialog1:false,
        clipped: false,
        drawer: false,
        fixed: false,
        items: [
          {
            icon: 'mdi-home',
            title: 'Home',
            to: '/'
          },
          {
            icon: 'mdi-apps',
            title: 'Productos',
            to: '/products'
          },
          {
            icon: 'mdi-apps',
            title: 'Nuevos',
            to: '/products/news'
          },
          {
            icon: 'mdi-apps',
            title: 'Configuración',
            to: '/edit'
          }
        ],
        miniVariant: false,
        right: true,
        rightDrawer: false,
        title: 'Vuetify.js'
      }
    },
  
    redirect_to_login(){
      window.location.href = '#';
    },
  methods: {
    salir() {
      this.dialog1 = true;
      axios.get('http://localhost:8000/forecast/salir');
    }
  }
}
  </script>
  