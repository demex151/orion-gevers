import test from "node:test";
import assert from "node:assert/strict";
import {normalizeOrbState,orbClassName} from "./orbState.js";

test("maps existing GEVER runtime statuses to visual life states",()=>{
 assert.equal(normalizeOrbState("ESPERANDO"),"idle");
 assert.equal(normalizeOrbState("ESCUCHANDO"),"listening");
 assert.equal(normalizeOrbState("PENSANDO"),"thinking");
 assert.equal(normalizeOrbState("PREPARANDO_VOZ"),"thinking");
 assert.equal(normalizeOrbState("HABLANDO"),"speaking");
});

test("unknown runtime status remains safely idle",()=>{
 assert.equal(normalizeOrbState("whatever"),"idle");
 assert.equal(orbClassName("HABLANDO"),"is-speaking");
});
