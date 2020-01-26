<template>
  <div class="root-agg">
    <div class="research" v-for="research in data">
      <div class="research-title">{{research.title_research}}</div>
      <div class="research-date" v-for="res in research.result">
        <div class="research-date-title">{{res.date}}:</div>
        <span class="research-group" v-for="g in res.data" v-if="non_empty_group(g)">
          <span class="research-group-title" v-if="g.group_title !== ''">
            {{fix_space(g.group_title)}}<span v-if="non_empty_fields(g)">:</span></span>
          <span class="group-field" v-for="(f, fi) in g.fields" v-if="f.value !== ''">
            <span class="group-field-title" v-if="f.title_field !== ''">{{fix_space(f.title_field)}}:</span><span
            v-html="fix_html(f.value)"/><span v-if="fi + 1 < g.fields.length">; </span></span>.
        </span>
      </div>
    </div>
  </div>
</template>

<script>
  import stationar_point from '../api/stationar-point'

  export default {
    props: {
      pk: {},
      extract: {
        type: Boolean,
        default: false
      },
      r_type: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        data: []
      }
    },
    mounted() {
      this.load()
    },
    methods: {
      async load() {
        this.data = await stationar_point.aggregateDesc(this, ['pk', 'extract', 'r_type'])
      },
      fix_html(v) {
        let lv = v;
        lv = lv.replaceAll('<', '&lt;').replaceAll('>', '&gt;');
        lv = lv.replaceAll('&lt;sub&gt;', '<sub>');
        lv = lv.replaceAll('&lt;/sub&gt;', '</sub>');
        lv = lv.replaceAll('&lt;sup&gt;', '<sup>');
        lv = lv.replaceAll('&lt;/sup&gt;', '</sup>');
        lv = lv.replaceAll('\n', '<br/>');
        return lv.trim();
      },
      fix_space(v) {
        return v.replace(' ', ' ')
      },
      non_empty_group(g) {
        if (g.group_title !== '') {
          return true;
        }

        return this.non_empty_fields(g);
      },
      non_empty_fields(g) {
        for (const f of g.fields) {
          if (f.value !== '') {
            return true;
          }
        }

        return false;
      }
    },
  }
</script>

<style scoped lang="scss">
  .root-agg {
    line-height: 1.5;
  }

  .research {
    margin-bottom: 10px;

    &-title {
      font-weight: bold;
      font-size: 110%;
    }

    &-date {
      text-align: justify;
    }

    &-group-title {
      font-weight: bold;
    }
  }

  .research-date-title {
    font-weight: bold;
  }

  .root-agg {
    max-width: 21cm;
  }
</style>