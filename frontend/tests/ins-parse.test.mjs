import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const componentSource = await readFile(
  new URL('../src/components/InsParse.vue', import.meta.url),
  'utf8',
)

test('获取最新视频不会重置用户取消的时间筛选', () => {
  assert.match(componentSource, /const onlyFresh = ref\(true\)/)
  assert.doesNotMatch(componentSource, /onlyFresh\.value\s*=\s*true/)
})
