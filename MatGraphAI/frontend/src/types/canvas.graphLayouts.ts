export const graphLayouts = [
    {
        name: "breadthfirst",
        spacingFactor: 175,
        directed: true,
    },
    {
        name: "concentric",
        minNodeSpacing: 50,
        spacingFactor: 3
    },
    {
        name: "grid",
        rows: 3,
    },
    {
        name: "fcose", // old
        animate: false,
        idealEdgeLength: 200,
        nodeSeparation: 2000,
        nodeRepulsion: 500_000,
        edgeElasticity: .45,
        numIter: 0,
        tile:false,
    },
    {
        name: "fcose",
        animate: false,
        idealEdgeLength: 200,
        // nodeSeparation: 2000,
        nodeRepulsion: 1_000_000,
        edgeElasticity: .25,
        numIter: 1000,
        tile:false,
        nestingFactor: 0.1,
        gravity: 0.05,
        gravityRange: 20,
        gravityCompound: 1,
        gravityCompoundRange: 1.5,
        tilingPaddingVertical: 10,
        tilingPaddingHorizontal: 10,
        initialEnergyOnIncremental: 0.5,
    },

]

