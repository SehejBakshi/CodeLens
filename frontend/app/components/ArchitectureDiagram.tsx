"use client";
import "@hpcc-js/wasm"; 
import { useEffect, useRef } from "react";
import { graphviz } from "d3-graphviz";
import * as d3 from "d3";

export default function ArchitectureDiagram({ architecture }: { architecture: any }) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!architecture?.length || !ref.current) return;

    const dot = architecture;
    if (!dot) return;

    // Clear previous diagram
    d3.select(ref.current).selectAll("*").remove();

    const viz = graphviz(ref.current)
      .engine("dot")
      .renderDot(dot);

    // Optional: Add zoom and pan behavior
    const svg = ref.current.querySelector("svg");
    if (svg) {
      const g = d3.select(svg).select("g");
      d3.select(svg).call(
        d3.zoom<SVGSVGElement, unknown>()
          .scaleExtent([0.1, 2])
          .on("zoom", (event) => {
            g.attr("transform", event.transform.toString());
          })
      );
    }
  }, [architecture]);

  return (
    <div className="w-full flex flex-col gap-2 items-center">
      <h3 className="font-semibold text-gray-100">Architecture Diagram</h3>
      <div
        ref={ref}
        className="w-full h-[600px] overflow-auto bg-gray-900 rounded-xl p-4"
      />
    </div>
  );
}
