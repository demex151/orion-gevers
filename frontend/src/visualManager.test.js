import test from "node:test";
import assert from "node:assert/strict";

import {
  createVisualState,
  openPanel,
  updatePanel,
  minimizePanel,
  closePanel,
  closeAllPanels,
} from "./visualManager.js";

test("assigns safe slots and never keeps more than three panels", () => {
  let state=createVisualState();
  state=openPanel(state,{id:"agenda",type:"agenda",title:"Agenda",data:{}});
  state=openPanel(state,{id:"leads",type:"leads",title:"Leads",data:{}});
  state=openPanel(state,{id:"metrics",type:"metrics",title:"Métricas",data:{}});
  assert.deepEqual(state.panels.map(p=>p.slot),["upper-right","lower-left","lower-right"]);
  const previous=state;
  state=openPanel(state,{id:"progress",type:"progress",title:"Progreso",data:{}});
  assert.equal(state.panels.length,3);
  assert.deepEqual(state.panels.map(p=>p.id),["leads","metrics","progress"]);
  assert.notEqual(state,previous);
});

test("updates minimizes and closes panels immutably", () => {
  const initial=openPanel(createVisualState(),{id:"agenda",type:"agenda",title:"Agenda",data:{count:1}});
  const updated=updatePanel(initial,"agenda",{title:"Agenda de hoy",data:{count:2}});
  assert.equal(updated.panels[0].title,"Agenda de hoy");
  assert.equal(initial.panels[0].title,"Agenda");
  const minimized=minimizePanel(updated,"agenda");
  assert.equal(minimized.panels[0].minimized,true);
  const closed=closePanel(minimized,"agenda");
  assert.equal(closed.panels.length,0);
  assert.equal(closeAllPanels().panels.length,0);
});

test("reopening an existing panel updates it and makes it most recent", () => {
  let state=createVisualState();
  state=openPanel(state,{id:"agenda",type:"agenda",title:"Agenda",data:{count:1}});
  state=openPanel(state,{id:"leads",type:"leads",title:"Leads",data:{}});
  state=openPanel(state,{id:"agenda",type:"agenda",title:"Agenda actualizada",data:{count:2}});
  assert.deepEqual(state.panels.map(p=>p.id),["leads","agenda"]);
  assert.equal(state.panels[1].title,"Agenda actualizada");
  assert.equal(state.panels[1].slot,"lower-left");
});
