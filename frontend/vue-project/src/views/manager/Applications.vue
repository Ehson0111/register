<template>
    <div class="applications-view">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Заявки</h1>
            <p class="text-gray-600">Заявки</p>
        </div>

            
    </div>

</template>>

<script setup Lang="ts">
import { defineComponent } from '@vue/composition-api'
import { ref, shallowReactive } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '../../composables/useToast'
 
import applicationsService, {
    type Applications,
} from  "../../../src/services/applications";
const loading =ref(false)

const allApplications=ref<A>
// import 

const loadAllApplications = async () => {
    try {
        loading.value =true;
        allApplications.value=await applicationsService.getApplications();
    }catch(error){
        console.error("Ошибка загрузки заявок",error);
        showError("не удалось загрузить заявок");

    }finally {
        loading.value=false;
    }
};
</script>
 