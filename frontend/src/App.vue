<script setup>

import {ref} from "vue"


const image = ref(null)
const loading = ref(false)
const message = ref("")


async function scanFingerprint(){

    loading.value = true
    message.value = "Place your finger on scanner..."


    try{

        const response =
            await fetch(
                "http://localhost:8000/capture",
                {
                    method:"POST"
                }
            )


        const data =
            await response.json()


        image.value =
  "http://127.0.0.1:8000"
  + data.image
  + "?t="
  + Date.now()


        message.value =
            "Fingerprint captured successfully"


    }
    catch(error){

        message.value =
            error.message

    }


    loading.value = false

}


</script>



<template>

<div class="container">


<h1>
CS9711 Fingerprint Scanner
</h1>


<button
@click="scanFingerprint"
:disabled="loading"
>

{{loading ?
"Scanning..." :
"Scan Fingerprint"}}

</button>



<h3>
{{message}}
</h3>



<div v-if="image">

<h2>
Captured Image
</h2>


<img
  :src="image"
  class="fingerprint"
/>


</div>


</div>


</template>



<style scoped>

.container{

text-align:center;
font-family:Arial;
margin-top:15px;

}


button{

font-size:20px;
padding:15px 40px;
border-radius:10px;
cursor:pointer;

}


img{

margin-top:20px;
border:3px solid black;
image-rendering:auto;

}


</style>