import test from "node:test";
import assert from "node:assert/strict";
import { normalizePanelContent } from "./visualPanelModel.js";

test("normalizes agenda content",()=>{const model=normalizePanelContent({type:"agenda",data:{items:[{time:"09:00",title:"Estimado"}]}});assert.equal(model.kind,"agenda");assert.equal(model.rows[0].primary,"09:00");assert.equal(model.rows[0].secondary,"Estimado")});
test("normalizes leads content",()=>{const model=normalizePanelContent({type:"leads",data:{items:[{name:"Cliente",status:"HOT",service:"Interior"}]}});assert.equal(model.kind,"leads");assert.equal(model.rows[0].primary,"Cliente");assert.match(model.rows[0].secondary,/HOT/) });
test("normalizes metrics progress communications and generic content",()=>{assert.equal(normalizePanelContent({type:"metrics",data:{items:[{label:"Leads",value:"3"}]}}).kind,"metrics");assert.equal(normalizePanelContent({type:"progress",data:{value:42,label:"Buscando"}}).progress,42);assert.equal(normalizePanelContent({type:"communications",data:{items:[{name:"María",message:"Hola"}]}}).rows[0].primary,"María");assert.equal(normalizePanelContent({type:"other",data:{text:"Resultado"}}).text,"Resultado")});
