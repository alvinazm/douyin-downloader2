import test from 'node:test'
import assert from 'node:assert/strict'
import { isInstagramCreatorReelsUrl } from '../src/utils/url.ts'

test('识别 Instagram 作者 reels 列表链接', () => {
  assert.equal(
    isInstagramCreatorReelsUrl('https://www.instagram.com/alivn.azm/reels/'),
    true,
  )
  assert.equal(
    isInstagramCreatorReelsUrl('https://instagram.com/alivn.azm/reels?hl=en'),
    true,
  )
})

test('不把 Instagram 单条视频链接误判为作者列表', () => {
  assert.equal(
    isInstagramCreatorReelsUrl('https://www.instagram.com/reel/DvoyPcWD3t8/'),
    false,
  )
  assert.equal(
    isInstagramCreatorReelsUrl('https://www.instagram.com/alivn.azm/'),
    false,
  )
})
