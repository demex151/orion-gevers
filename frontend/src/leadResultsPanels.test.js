import test from 'node:test';
import assert from 'node:assert/strict';
import {leadResultsPanels} from './leadResultsPanels.js';

test('builds summary, classification and opportunity panels from stored results',()=>{
 const panels=leadResultsPanels({run:{raw_findings:36,accepted_leads:3,rejected_findings:33,hot_count:2,warm_count:1,prospect_count:0},leads:[{name:'Ana',classification:'HOT',score:91,location:'Myrtle Beach',service:'Interior painting',evidence:'Looking for a painter this week',source_url:'https://example.com/a'}]});
 assert.equal(panels.length,3);
 assert.equal(panels[0].metrics[0][1],36);
 assert.deepEqual(panels[1].metrics,[['HOT',2],['WARM',1],['PROSPECT',0]]);
 assert.equal(panels[2].items[0].name,'Ana');
 assert.equal(panels[2].items[0].score,91);
});

test('returns no panels when there is no completed search',()=>assert.deepEqual(leadResultsPanels(null),[]));
