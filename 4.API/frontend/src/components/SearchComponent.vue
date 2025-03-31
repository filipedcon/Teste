<template>
  <div class="search-container">
    <input v-model="query" @input="searchOperadora" placeholder="Buscar operadora..." class="search-input" />
    
    <div v-if="results.length > 0" class="results-container">
      <ul>
        <li v-for="(operadora, index) in results" :key="index" class="result-item">
          <h3>{{ operadora.Razao_Social }}</h3>
          <p><strong>Registro ANS:</strong> {{ operadora.Registro_ANS }}</p>
          <p><strong>CNPJ:</strong> {{ operadora.CNPJ }}</p>
          <p><strong>Modalidade:</strong> {{ operadora.Modalidade }}</p>
        </li>
      </ul>
    </div>

    <div v-else class="no-results">
      <p>Nenhum resultado encontrado</p>
    </div>
  </div>
</template>

<style scoped>
/* Container principal */
.search-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  text-align: center;
}

/* Estilo do input de busca */
.search-input {
  padding: 10px;
  font-size: 16px;
  margin-bottom: 20px;
  width: 100%;
  max-width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

/* Estilo do container de resultados */
.results-container {
  width: 100%;
  max-width: 600px;
  margin-top: 20px;
}

/* Estilo dos itens de resultado */
ul {
  list-style-type: none;
  padding: 0;
}

.result-item {
  background-color: #f9f9f9;
  margin: 10px 0;
  padding: 15px;
  border-radius: 8px;
}

h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

p {
  margin: 5px 0;
  font-size: 14px;
}

strong {
  font-weight: bold;
}

/* Estilo para o caso de não haver resultados */
.no-results {
  font-size: 18px;
  color: #555;
}
</style>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      query: '',
      results: [],
    };
  },
  methods: {
      async searchOperadora() {
    console.log('Buscando por:', this.query);  // Adicionando o log para verificar a query
    if (this.query.trim() === '') {
      this.results = [];
      return;
    }

    try {
      const response = await api.get('/busca/', {
        params: { q: this.query },
      });

      console.log('Resposta da API:', response.data);  // Verificando os dados recebidos da API

      if (response.data.resultado && response.data.resultado.length > 0) {
        this.results = response.data.resultado;  // Acessando o campo `resultado` dentro da resposta
      } else {
        this.results = [];
      }
    } catch (error) {
      console.error('Erro ao buscar operadora:', error);
    }
  }
  },
};
</script>

<style scoped>
.search-container {
  text-align: center;
  padding: 20px;
}

input {
  padding: 10px;
  margin: 20px 0;
  width: 300px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 10px;
  border: 1px solid #ddd;
  margin: 5px 0;
  border-radius: 5px;
}
</style>
