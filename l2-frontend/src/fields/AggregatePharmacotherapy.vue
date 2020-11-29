<template>
  <div class="root-agg">
    <table class="table table-responsive table-bordered table-condensed">
      <colgroup>
        <col style="width: 300px" />
        <col v-for="d in dates" :key="d" />
      </colgroup>
      <thead>
      <tr>
        <th rowspan="2">Наименование ЛП</th>
        <th v-for="d in dates" :key="d">{{d}}</th>
      </tr>
      <tr>
        <th v-for="d in dates" :key="d" class="cl-td">
          <div class="time" v-for="t in timesInDates[d]" :key="t">
            {{t.split(':')[0]}}
          </div>
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="r in rows">
        <td>
          <div class="drug" :class="{cancel: r.cancel}">{{r.drug}}</div>
          <span class="badge badge-primary" title="Форма выпуска" v-tippy>{{r.form_release}}</span>
          <span class="badge badge-primary" title="Способ применения" v-tippy>{{r.method}}</span>
          <span class="badge badge-info" title="Дозировка" v-tippy>{{r.dosage}}</span>
          <span class="badge badge-light" title="Дата создания" v-tippy>{{r.created_at}}</span>
          <template v-if="can_cancel">
            <a class="badge badge-secondary" href="#" v-if="!r.cancel" @click.prevent="cancelRow(r.pk, true)">
              <i class="fa fa-circle"/> отменить ЛП
            </a>
            <a class="badge badge-secondary" href="#" v-else @click.prevent="cancelRow(r.pk, false)">
              <i class="fa fa-circle"/> вернуть ЛП
            </a>
          </template>
        </td>
        <td v-for="d in dates" :key="d" class="cl-td">
          <PharmacotherapyTime :data="r.dates[d][t]" v-for="t in timesInDates[d]" :key="t" />
        </td>
      </tr>
      <tr v-if="rows.length === 0">
        <td>Нет данных</td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
  import api from '@/api'
  import PharmacotherapyTime from "@/fields/PharmacotherapyTime";
  import * as action_types from "@/store/action-types";

  export default {
    components: {PharmacotherapyTime},
    props: {
      direction: {},
    },
    data() {
      return {
        rows: [],
        dates: [],
        times: [],
        timesInDates: {},
      }
    },
    async mounted() {
      await this.load()
      this.$root.$on('pharmacotherapy-aggregation:reload', () => this.load());
    },
    computed: {
      can_cancel() {
        for (let g of (this.$store.getters.user_data.groups || [])) {
          if (g === 'Врач стационара' || g === "Admin") {
            return true
          }
        }
        return false
      },
    },
    methods: {
      async load() {
        await this.$store.dispatch(action_types.INC_LOADING);
        const {
          result,
          dates,
          times,
          timesInDates,
        } = await api('procedural-list/get-procedure', this, 'direction');
        this.rows = result;
        this.dates = dates;
        this.times = times;
        this.timesInDates = timesInDates;
        await this.$store.dispatch(action_types.DEC_LOADING);
      },
      async cancelRow(pk, cancel) {
        if (cancel) {
          try {
            await this.$dialog.confirm('Вы действительно хотите отменить назначение?')
          } catch (_) {
            return
          }
        } else {
          try {
            await this.$dialog.confirm('Вы действительно хотите вернуть назначение?')
          } catch (_) {
            return
          }
        }
        await this.$store.dispatch(action_types.INC_LOADING);
        const {ok, message} = await api('procedural-list/procedure-cancel', {pk, cancel});
        if (ok) {
          okmessage(message);
          this.$root.$emit('pharmacotherapy-aggregation:reload')
        } else {
          errmessage(message);
        }
        await this.$store.dispatch(action_types.DEC_LOADING);
      },
    },
  }
</script>

<style scoped lang="scss">
.time {
  display: inline-block;
  width: 30px;
  text-align: center;
  height: 24px;
  font-weight: normal;
  font-size: 12px;
  vertical-align: bottom;

  //&:nth-child(odd) {
  //  background-color: rgba(#000, .045);
  //}
}

.root-agg {
  overflow-x: auto;
}

a.badge:hover {
  background-color: #5f6267;
}

table {
  min-width: 100%;
  max-width: none;
  width: auto;

  .cl-td {
    white-space: nowrap;
  }
}

.drug {
  width: 296px;

  &.cancel:not(:hover) {
    text-decoration: line-through;
  }
}
</style>