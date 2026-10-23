import { BenchmarkForm } from './components/BenchmarkForm';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Axiom Observatory</h1>
        <p className="subtitle">TokenSpeed Inference Benchmarking</p>
      </header>
      <main className="app-main">
        <BenchmarkForm />
      </main>
      <footer className="app-footer">
        <p>Axiom Observatory &copy; 2024 Ryan Vo (ryandtvo@gmail.com)</p>
      </footer>
    </div>
  );
}

export default App;
