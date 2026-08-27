import test from "node:test";
import assert from "node:assert/strict";
import {inferVisualIntent} from "./visualIntent.js";

test("opens agenda only when agenda is requested",()=>{assert.deepEqual(inferVisualIntent("revisa mi agenda"),{action:"open",type:"agenda"})});
test("opens leads only when opportunities are requested",()=>{assert.deepEqual(inferVisualIntent("muéstrame los clientes que encontraste"),{action:"open",type:"leads"})});
test("opens metrics and progress contextually",()=>{assert.deepEqual(inferVisualIntent("muéstrame las métricas"),{action:"open",type:"metrics"});assert.deepEqual(inferVisualIntent("cómo va el progreso"),{action:"open",type:"progress"})});
test("does not open a panel for ordinary conversation",()=>{assert.equal(inferVisualIntent("hola gever cómo estás"),null);assert.equal(inferVisualIntent("gracias"),null)});
test("closes contextual panels when explicitly requested",()=>{assert.deepEqual(inferVisualIntent("cierra los paneles"),{action:"close-all"})});
