import test from "node:test";
import assert from "node:assert/strict";
import {telemetryPanels} from "./leadHunterTelemetry.js";

test("returns no panels while idle",()=>{
 assert.deepEqual(telemetryPanels(null),[]);
 assert.deepEqual(telemetryPanels({state:"idle"}),[]);
});

test("labels the results panel as the final result when completed",()=>{
 const panels=telemetryPanels({state:"completed",classifications:{HOT:1,WARM:0,PROSPECT:0}});
 assert.equal(panels[2].title,"RESULTADO FINAL");
});

test("labels the results panel as a failed search instead of pretending it finished",()=>{
 const panels=telemetryPanels({state:"failed",error:"DDGS search failed: timeout",classifications:{HOT:0,WARM:0,PROSPECT:0}});
 assert.equal(panels[2].title,"BÚSQUEDA FALLIDA");
 assert.notEqual(panels[2].title,"RESULTADO FINAL");
});

test("keeps showing the in-progress label while actively searching",()=>{
 const panels=telemetryPanels({state:"active",active_stage:"search",classifications:{}});
 assert.equal(panels[2].title,"OPORTUNIDADES");
});
