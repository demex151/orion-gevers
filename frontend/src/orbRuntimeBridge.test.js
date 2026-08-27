import test from "node:test";
import assert from "node:assert/strict";
import {createOrbRuntimeBridge} from "./orbRuntimeBridge.js";

test("publishes runtime status without coupling to audio",()=>{
 const events=[];
 const target={dispatchEvent:event=>events.push(event),addEventListener(){},removeEventListener(){}};
 const bridge=createOrbRuntimeBridge(target);
 bridge.publish("HABLANDO");
 assert.equal(events.length,1);
 assert.equal(events[0].type,"gever:runtime-status");
 assert.equal(events[0].detail.status,"HABLANDO");
});
