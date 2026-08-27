import test from 'node:test';
import assert from 'node:assert/strict';
import {nextPanelVisibility} from './leadPanelSpeechLifecycle.js';

test('keeps panels while GEVER is speaking and closes when speech ends',()=>{
 let state={visible:true,sawSpeaking:false};
 state=nextPanelVisibility(state,'speaking');
 assert.deepEqual(state,{visible:true,sawSpeaking:true});
 state=nextPanelVisibility(state,'idle');
 assert.deepEqual(state,{visible:false,sawSpeaking:true});
});

test('does not close before GEVER has actually started speaking',()=>{
 assert.deepEqual(nextPanelVisibility({visible:true,sawSpeaking:false},'thinking'),{visible:true,sawSpeaking:false});
});
