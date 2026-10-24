// DEMO CONTENT: all sources below are fictional/illustrative, written for the demo. Not real studies or lectures.
window.SEED = [
 {id:'econ', title:'Econ 101: Minimum wage essay', prompt:'In 600 words, argue whether a higher minimum wage reduces employment. Use at least two sources.',
  nextSrc:4, sources:[
  {id:'S1', kind:'lecture', title:'Lecture 7 (Prof. Reyes), price floors, 12:40-18:05',
   text:'A price floor set above the equilibrium price creates a surplus: at the higher price, sellers want to supply more than buyers want to buy. In the labour market the "price" is the wage, so a binding minimum wage can leave more people seeking work than there are jobs. Reyes stressed the word binding: a floor set below the market wage changes nothing. He also warned that the size of the effect depends on how elastic labour demand is, so the textbook diagram gives direction, not magnitude.'},
  {id:'S2', kind:'paper', title:'Study summary A (fictional): border-county comparison',
   text:'Comparing neighbouring counties where only one raised its minimum wage, the authors found employment in fast-food restaurants changed by less than one percent. They argue employers absorbed part of the cost through slightly higher prices and lower turnover. They caution that the result applies to modest increases in a growing economy.'},
  {id:'S3', kind:'paper', title:'Study summary B (fictional): large increase, small firms',
   text:'Looking at a large, rapid wage increase, the authors report that hours worked by low-wage employees at small firms fell by roughly six percent, while large firms showed no clear change. They conclude that firm size and the speed of the increase matter more than the headline wage level.'}]},
 {id:'cs', title:'CS FYP: Learning-rate schedules', prompt:'Explain why gradient descent often needs a learning-rate schedule, and when a constant rate is enough.',
  nextSrc:4, sources:[
  {id:'S1', kind:'lecture', title:'Lecture 4 (Dr. Okafor), step size and convergence, 21:10-29:30',
   text:'With a fixed step size on a smooth convex function, gradient descent converges if the step is small enough, but near the minimum a large step makes the iterates bounce around it instead of settling. Okafor drew the bowl with oscillating arrows: early on you want big steps to cover ground; later you want small steps to settle. Decaying the step size is the standard fix. A constant rate can be fine when the loss is well conditioned and you only need a rough answer.'},
  {id:'S2', kind:'handout', title:'Handout: common schedules',
   text:'Step decay multiplies the rate by a factor every few epochs. Exponential decay shrinks it smoothly. Cosine annealing lowers it along a cosine curve and can restart. Warm-up starts with a very small rate and increases it for the first iterations, which stabilises early training of large models.'},
  {id:'S3', kind:'note', title:'My notes: noisy gradients',
   text:'With stochastic gradients the noise does not shrink as you approach the minimum, so even a small constant rate leaves the iterate jittering in a ball around it. A decaying rate averages out the noise. Not sure how this interacts with momentum.'}]}
];
