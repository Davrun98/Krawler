# Development checkpoint reflection
Now that the code has reached a point that it's somewhat deliverable I'm taking a moment to reflect on the process to this point.

### Loyalty to original design
I'm quite surprised by how much of the original design holds up in the current version, the most significant variations are:
- `LinkRipper` doesn't exist anymore - it ended up being a very small amount of code so was aggregated into `LinkProcessor` 
- The callback pattern was removed and replaced with a return sequence - as the `LinkProcessor` took on more responsibility and the chain shortened it became the more sensible way to move that information back into the orchestrator

### Regrets (trade-offs)
Once I'd identified just how complicated certain elements of development would be (i.e. the loose restrictions on what an href looks like in HTML) I had to make some compromises to complete the basics.
- The logic isn't bulletproof, there are still bugs that I haven't ironed out
- I set my aspirations too high for a piece of code that was never intended to be completed - this has manifested as a pile of technical debt where speed compromised quality
- Test coverage was halted, ideally this code would have much more comprehensive testing with more edge cases considered
