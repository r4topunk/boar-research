// kld3: teacher-forced KL divergence of N test models vs a reference model over the answer tokens of dumped prompts.
// Usage: kld3 <items dir> <n_items> <ref.gguf> <test1.gguf> [test2.gguf ...]
// items dir holds NN.prompt.txt (chat-rendered, special tokens parsed) and NN.answer.txt (plain text; <|im_end|> appended as a special token).
// Per answer position i (predicting token t_i): KLD = sum_v p_ref(v) (log p_ref(v) - log p_test(v)); top1 = argmax equal; dp = p_test(t_i) - p_ref(t_i).
// Same definitions as llama-perplexity --kl-divergence, but scored on the answer tokens only (that tool scores the second half of each chunk).
#include "llama.h"
#include <cstdio>
#include <cmath>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <algorithm>
static std::string rd(const std::string & p){ std::ifstream f(p, std::ios::binary); std::stringstream s; s << f.rdbuf(); return s.str(); }
static std::vector<llama_token> tok(const llama_vocab * v, const std::string & t, bool special){
  std::vector<llama_token> o(t.size()+16);
  int n = llama_tokenize(v, t.c_str(), t.size(), o.data(), o.size(), false, special);
  if (n < 0) { o.resize(-n); n = llama_tokenize(v, t.c_str(), t.size(), o.data(), o.size(), false, special); }
  o.resize(n); return o;
}
static void logsoftmax(const float * x, int n, std::vector<double> & out){
  float mx = *std::max_element(x, x+n); double s = 0; for (int i=0;i<n;i++) s += std::exp((double)x[i]-mx);
  double ls = std::log(s) + mx; out.resize(n); for (int i=0;i<n;i++) out[i] = (double)x[i]-ls;
}
int main(int argc, char ** argv){
  if (argc < 5) return 2;
  std::string dir = argv[1]; int N = atoi(argv[2]);
  llama_log_set([](ggml_log_level, const char *, void *){}, nullptr);
  llama_backend_init();
  std::vector<llama_model*> M; std::vector<llama_context*> C;
  for (int a = 3; a < argc; a++){
    auto mp = llama_model_default_params(); mp.n_gpu_layers = 0;
    llama_model * m = llama_model_load_from_file(argv[a], mp); if (!m) { fprintf(stderr,"load fail %s\n", argv[a]); return 1; }
    auto cp = llama_context_default_params(); cp.n_ctx = 4096; cp.n_batch = 4096; cp.n_ubatch = 512; cp.n_threads = 4; cp.n_threads_batch = 4;
    llama_context * c = llama_init_from_model(m, cp); if (!c) return 1; M.push_back(m); C.push_back(c);
  }
  const llama_vocab * V = llama_model_get_vocab(M[0]); int nv = llama_vocab_n_tokens(V);
  int nt = M.size()-1;
  std::vector<double> sk(nt,0), sk2(nt,0), sd(nt,0); std::vector<long> agree(nt,0); long cnt = 0;
  printf("item\tmodel\tpos\ttok\tkld\ttop1\tdp\n");
  for (int it = 0; it < N; it++){
    char nm[64]; snprintf(nm,64,"%02d", it);
    auto P = tok(V, rd(dir+"/"+nm+".prompt.txt"), true);
    auto A = tok(V, rd(dir+"/"+nm+".answer.txt"), false);
    auto E = tok(V, "<|im_end|>", true); A.insert(A.end(), E.begin(), E.end());
    std::vector<llama_token> T = P; T.insert(T.end(), A.begin(), A.end());
    std::vector<std::vector<float>> L(M.size());
    for (size_t k = 0; k < M.size(); k++){
      llama_memory_clear(llama_get_memory(C[k]), true);
      std::vector<int8_t> dummy;
      llama_batch b = llama_batch_init(T.size(), 0, 1);
      for (size_t i = 0; i < T.size(); i++){ b.token[i]=T[i]; b.pos[i]=i; b.n_seq_id[i]=1; b.seq_id[i][0]=0; b.logits[i] = (i >= P.size()-1 && i < T.size()-1) ? 1 : 0; }
      b.n_tokens = T.size();
      if (llama_decode(C[k], b)) { fprintf(stderr,"decode fail\n"); return 1; }
      L[k].resize(A.size()*(size_t)nv);
      for (size_t j = 0; j < A.size(); j++){ const float * lg = llama_get_logits_ith(C[k], P.size()-1+j); std::copy(lg, lg+nv, L[k].begin()+j*nv); }
      llama_batch_free(b);
    }
    for (size_t j = 0; j < A.size(); j++){
      std::vector<double> lp; logsoftmax(&L[0][j*nv], nv, lp);
      int rtop = std::max_element(L[0].begin()+j*nv, L[0].begin()+(j+1)*nv) - (L[0].begin()+j*nv);
      for (int k = 0; k < nt; k++){
        std::vector<double> lq; logsoftmax(&L[k+1][j*nv], nv, lq);
        double kl = 0; for (int v=0; v<nv; v++){ double p = std::exp(lp[v]); if (p > 0) kl += p*(lp[v]-lq[v]); }
        int qtop = std::max_element(L[k+1].begin()+j*nv, L[k+1].begin()+(j+1)*nv) - (L[k+1].begin()+j*nv);
        double dp = std::exp(lq[A[j]]) - std::exp(lp[A[j]]);
        sk[k]+=kl; sk2[k]+=kl*kl; sd[k]+=dp; agree[k]+= (rtop==qtop);
        printf("%d\t%d\t%zu\t%d\t%.6f\t%d\t%.6f\n", it, k+1, j, A[j], kl, rtop==qtop, dp);
      }
      cnt++;
    }
    fprintf(stderr,"item %d done (P=%zu A=%zu)\n", it, P.size(), A.size());
  }
  for (int k = 0; k < nt; k++){
    double m = sk[k]/cnt, sdv = std::sqrt((sk2[k]/cnt - m*m)/cnt);
    fprintf(stderr,"SUMMARY model=%s tokens=%ld meanKLD=%.6f +-%.6f top1=%.3f%% meandp=%.4f%%\n", argv[4+k], cnt, m, sdv, 100.0*agree[k]/cnt, 100.0*sd[k]/cnt);
  }
}
