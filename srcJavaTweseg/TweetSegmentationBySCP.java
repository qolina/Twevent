/**
 * 
 */
//package tweseg;

import java.io.File;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Date;

/**
 * @author Chenliang Li [lich0020@ntu.edu.sg]
 *
 */
public class TweetSegmentationBySCP {
	
	private static final int N = 5; // up to 5-gram;
	private static final char SEPARATOR_CHAR = '_';
	public static Comparator<Double> DOUBLE_ASC = 
		new Comparator<Double>() {
		@Override
		public int compare(Double d1, Double d2) {
			// TODO Auto-generated
			// method stub
			return d1.compareTo(d2);
		}
	};
	
	private static String STOP_WORD_FILE = "../Tools/stoplist.dft";
	//private static String MS_GRAM_FILE = "../Tools/ngrams_prob_stock";
	private static String MS_GRAM_FILE = "../Tools/prob_ngrams_giga";
	private static String WIKI_GRAM_FILE = "../Tools/anchorProbFile_all";
	private static double MIN_LOG = -Math.pow(10, 20);
	
	private Set<String> stopwords;
	private HashMap<String, Double> msProbMap;
	private HashMap<String, Double> wikiProbMap;
	
	public TweetSegmentationBySCP(){
		stopwords = new HashSet<String>();
		try {
			File file = new File(STOP_WORD_FILE);
			if (file.exists()) {
				// load the stop words into the set "stopwords";
                // added by qin
                BufferedReader buffReader = new BufferedReader(new FileReader(file));
                String lineStr = null;
                while((lineStr = buffReader.readLine()) != null){
                    stopwords.add(lineStr);
                }
                buffReader.close();
			}
		} catch (Exception e) {
//			LOG.error("loading stopword file error.");
			stopwords = new HashSet<String>();
		}
        Date date = new Date();
        System.out.println("## Loading ends. " + stopwords.size() + " stopwords are loaded at " + date);
	}
	
    // added by qin
	public int loadMSNGramMap(String gramFilePath){
        msProbMap = new HashMap<String, Double>();
		try {
			File file = new File(gramFilePath);
			if (file.exists()) {
                BufferedReader buffReader = new BufferedReader(new FileReader(file));
                String lineStr = null;
                while((lineStr = buffReader.readLine()) != null){
                    double prob = Double.valueOf(lineStr.substring(0, lineStr.indexOf("\t")));
                    String gram = lineStr.substring(lineStr.indexOf("\t"));
                    gram = gram.trim();
                    msProbMap.put(gram, prob);
//                    System.out.println(lineStr);
//                    System.out.println("#" + gram + "# " + prob);
                }
                buffReader.close();
			}
		} catch (Exception e) {
            msProbMap = new HashMap<String, Double>();
            return -1;
		}
        Date date = new Date();
        System.out.println("## Loading ends. " + msProbMap.size() + " grams' ms prob are loaded at " + date);
        return 1;
    }

    // added by qin
	public int loadWikiGramMap(){
        wikiProbMap = new HashMap<String, Double>();
		try {
			File file = new File(WIKI_GRAM_FILE);
			if (file.exists()) {
                BufferedReader buffReader = new BufferedReader(new FileReader(file));
                String lineStr = null;
                while((lineStr = buffReader.readLine()) != null){
                    double prob = Double.valueOf(lineStr.substring(0, lineStr.indexOf(" ")));
                    String gram = lineStr.substring(lineStr.indexOf(" "));
                    gram = gram.trim();
                    wikiProbMap.put(gram, prob);
//                    System.out.println(lineStr);
//                    System.out.println("#" + gram + "# " + prob);
                }
                buffReader.close();
			}
		} catch (Exception e) {
            wikiProbMap = new HashMap<String, Double>();
            return -1;
		}
        Date date = new Date();
        System.out.println("## Loading ends. " + wikiProbMap.size() + " grams' wiki prob are loaded at " + date);
        return 1;
    }

	private List<String> tokenizeTweet(String tweet){
		tweet = cleanTweet(tweet);
		tweet = tweet.replaceAll("@[\\p{Alnum}\\p{Punct}]+", "@USERNAME");
		
		StringBuilder buffer = new StringBuilder(tweet);
		int index = -1;
		do {
			index = buffer.indexOf("@USERNAME", index+1);
			if ( index > 0 && 
					Character.isLetter(buffer.charAt(index-1))){
				buffer.replace(index, index+9, " ");
			}
		} while (index >= 0);
		tweet = buffer.toString();
		
		// normalize the urls
		tweet = tweet.replaceAll(
				"http://[\\p{Alnum}\\p{Punct}]+", "@http").trim();
		
		// normalize RT labels
		tweet = tweet.replaceAll("[rR][tT]\\s+", " ").trim();
		tweet = tweet.replaceAll("\\s", " ");
		
		tweet = tweet.replaceAll("#[\\p{Alnum}p{Punct}]+", " ");
		tweet = tweet.replace("@USERNAME", " ");
		tweet = tweet.replace("@http", " ").trim().toLowerCase();
		
		List<String> tokenlist = new ArrayList<String>();
		String[] tokens = tweet.split("\\s");
		for ( int i = 0; i < tokens.length; i++ ){
			String token = tokens[i];
			if ( !stopwords.contains(token)){
                if (token.length() > 1){ // omit 1-length word, added by qin
                    String testStr = token.replaceAll("_", " ");
                    if (testStr.trim().isEmpty() == true){// omit words "___" 
                        continue;
                    }
                    tokenlist.add(token);
                }
			}
		}
		
		return tokenlist;
	}
	
	public List<ScoredSegment> tweetSegmentBySCP(
			String tweet){
		List<String> tokenlist = tokenizeTweet(tweet);
		
		int length = tokenlist.size();
		if ( length == 0 )
			return null; // nothing to segment
		
		List<Map<List<Integer>, Double>> segmentList = 
			new ArrayList<Map<List<Integer>, Double>>();
		
		double[][] probMatrix = MSNGramProb(tokenlist, N);
		
		for (int i = 0; i < length; i++) {
			Map<List<Integer>, Double> subsegmentMap = 
					new HashMap<List<Integer>, Double>();
			
			String ngram = ngram(tokenlist, 0, i);
			if (i < N) {
				List<Integer> subsegment = new ArrayList<Integer>();
				subsegment.add(i);

				double score = Double.NEGATIVE_INFINITY;
				score = 
					stickinessWithWikiAndLengthNormAndSCP(ngram, probMatrix, 0,
						i);

                String listStr = numListToStr(subsegment);
//                System.out.println("current[0,i]: " + listStr + " -> " + score);
//                System.out.println("# Gram[0,i): " + ngram + " -> " + score);
				subsegmentMap.put(subsegment, score);
			}

			if (i > 0) { // dynamic programming
				for (int j = 0; j < i; j++) { // iterate over all prior sgt
					if ( i - j > N )
						continue;
					
					ngram = ngram(tokenlist, j+1, i);
					Map<List<Integer>, Double> priorsgtMap = segmentList.get(j);
					double score = 
						stickinessWithWikiAndLengthNormAndSCP(
							ngram,
							probMatrix, j + 1, i);

					for (List<Integer> priorsgt : priorsgtMap.keySet()) {
						Double value = priorsgtMap.get(priorsgt);
                        String listStr = numListToStr(priorsgt);
//                        System.out.println("prior[0,j]: " + listStr + " -> " + value + " + " + score);
						value += score;
						List<Integer> sgt = mergeTwoSeg(priorsgt, i);
						subsegmentMap.put(sgt, value);
                        listStr = numListToStr(sgt);
//                        System.out.println("merged[0,i]: " + listStr + " -> " + value);
//                        System.out.println("# Gram[j+1,i] + Gram[i,L): " + ngram + " + " + ngram(tokenlist, i, length-1) + " -> " + value)
					}
				}
			}

			/* filter out lower scored segment */
			int k = 5;
			List<KeyValueObj<Double, List<Integer>>> topN = 
					topN(subsegmentMap, DOUBLE_ASC, k);
			subsegmentMap.clear();
			for (KeyValueObj<Double, List<Integer>> kvo : topN) {
				subsegmentMap.put(kvo.getValue(), kvo.getKey());
                String listStr = numListToStr(kvo.getValue());
//                System.out.println("Top 5: " + listStr + " -> " + kvo.getKey());
			}

			segmentList.add(subsegmentMap);
		}

		Map<List<Integer>, Double> finalsgt = segmentList.get(length - 1);
		List<Integer> bestsgt = null;
		double max = Double.NEGATIVE_INFINITY;
		for (List<Integer> sgt : finalsgt.keySet()) {
			double score = finalsgt.get(sgt);
			if (Double.compare(score, max) > 0) {
				bestsgt = sgt;
				max = score;
			}
		}

//		LOG.info("best score: " + max);
		int[] marks = new int[length];
		int index = 0;
		for (int j = 0; j < marks.length; j++) {
			int pos = bestsgt.get(index);
			if (j == pos) {
				marks[j] = 1;
				index++;
			}
		}

		List<List<String>> segment = new ArrayList<List<String>>();
		List<String> subSeg = new ArrayList<String>();
		for (int i = 0; i < marks.length; i++) {
			subSeg.add(tokenlist.get(i));
			if (marks[i] == 1) {
				segment.add(subSeg);
				subSeg = new ArrayList<String>();
			}
		}

		List<ScoredSegment> segmentWithScore = 
				new ArrayList<ScoredSegment>();
		
		int s = 0;
		for ( int i = 0; i < segment.size(); i++ ){
			List<String> subseg = segment.get(i);
			int e = s + subseg.size();
			String ngram = ngram(tokenlist, s, e-1);
			double score = 
				stickinessWithWikiAndLengthNormAndSCP(
					ngram, probMatrix, s, e-1);
			
			segmentWithScore.add(new ScoredSegment(subseg, score));
			s = e;
		}
		
		return segmentWithScore;
	}
	
	/**
	 * Return a matrix of n-gram probabilities.
	 * The matrix has a L x L size, where L is the length of 
	 * the specified tokenlist. The entry (i,j) refers to the 
	 * probability of n-gram w_i...w_j based on the MS N-Gram 
	 * Service. Note that the indices i, j refer to the words
	 * located at the i, j position of the specified tokenlist.
	 * @param tokenlist
	 * @param m
	 * @return
	 */
	private double[][] MSNGramProb(
			List<String> tokenlist, int m){
        // completed by qin
        int L = tokenlist.size();
        double[][] probMatrix = new double[L][L];
        for (int i = 0; i < L; i ++){
            for (int j = i; j < L; j ++){
                if (j-i >= m){
                    probMatrix[i][j] = MIN_LOG;
                    continue;
                }
                String gram_ = ngram(tokenlist, i, j);
                String gram = gram_.replaceAll("[_]+", "_");
                gram = gram.replaceAll("^_", "");
                gram = gram.replaceAll("_$", "");
                gram = gram.trim();
//                System.out.println("## Gram: #" + gram + "# from #" + gram_+"#");
                double prob = -100.0;
                if (msProbMap.containsKey(gram)){
					prob = msProbMap.get(gram);
                } 
				//else {
                //    System.out.println("##MS N-Gram prob not existed: #" + gram + "# extracted from #" + gram_+"#");
				//}
                probMatrix[i][j] = Math.pow(10, prob);
            }
        }
		return probMatrix;
	}
	
	private List<Integer> mergeTwoSeg(List<Integer> prior, int index) {
		List<Integer> list = new ArrayList<Integer>();
		for (int i = 0; i < prior.size(); i++) {
			list.add(prior.get(i));
		}

		list.add(index);
		return list;
	}
	
	private double stickinessWithWikiAndLengthNormAndSCP(
			String ngram, double[][] probMatrix, int s, int e){
		double score = 
			stickinessWithLengthNormBySCP(probMatrix, s, e);
		double keyphraseness = 0.0;
		int length = e-s+1;
		try {
			keyphraseness = wikiKeyphraseness(ngram);
		} catch ( Exception ex ){
			ex.printStackTrace();
			keyphraseness = 0.0;
		}
		
		return score * Math.exp(keyphraseness);
	}
	
	private double stickinessWithLengthNormBySCP(
			double[][] probMatrix, int s, int e){
		double score = stickinessBySCP(
				probMatrix, s, e);
//		double score = stickinessByGFSCP(
//				probMatrix, s, e);
		score = 2 / (1+Math.exp(-score));
		int n = e - s + 1;
		if ( n > 1 ){
			score = score * (n-1) / n;
		}

		return score;
	}
	
	private double stickinessBySCP(
			double[][] probMatrix, int s, int e){
		final double instead = Double.NaN;
		int n = e - s + 1;
		double score = 0;

		double nprob = probMatrix[s][e];

		if (n == 1) { // unigram
			score = log10(nprob)*2;
		} else { // n-gram
			double avg = 0.0;
			for (int i = s; i < e; i++) {
				double inprob = probMatrix[i + 1][e];
				double iprob = probMatrix[s][i];
				avg += (inprob*iprob);
			}
			avg = avg / (n-1);
			score = nprob * nprob / avg;
			score = log10(score);
		}

		return score;
	}
	
	private double log10(double value) {
		if (Double.compare(value, 0.0) <= 0) {
			return MIN_LOG;
		}

		return Math.log10(value);
	}
	
	/**
	 * Return the keyphraseness of the specified phrase;
	 * @param ngram
	 * @return
	 */
	private double wikiKeyphraseness(String ngram){
		// must be implemented...
        double prob = 0.0;
        String gram = ngram.replaceAll("[_]+", " ");
        gram = gram.replaceAll("\\s+", " ");
        gram = gram.trim();
        if (! wikiProbMap.containsKey(gram)){
//            System.out.println("##Wiki anchor text not existed: #" + gram + "# extracted from #" + ngram+"#");
        }
        else{
            prob = wikiProbMap.get(gram);
//            System.out.println("##Wiki anchor text : #" + gram + "#:" + prob);
        }
		return prob;
	}
	
	/**
	 * Clear tweet by removing the specific characters
	 * specified by '\'
	 * @param text
	 * @return
	 */
	private static String cleanTweet(String text){
		StringBuilder buffer = new StringBuilder();
		for ( int i = 0; i < text.length(); i++ ){
			char value = text.charAt(i);
			if ( value != '\\' || i == text.length() - 1 ){
				buffer.append(value);
			} else {
				char suffix = text.charAt(i+1);
				if ( suffix == 't' || suffix == 's' || 
						suffix == 'n' || suffix == '\"' ||
						suffix == 'r' ){
					buffer.append(' ');
					i += 1; // jump off
				}
			}
		}
		
		return buffer.toString();
	}
	
	/**
	 * Gets the ngram from the specified token list.
	 * @param tokenlist
	 * @return
	 */
	public static String ngram(List<String> tokenlist){
		return ngram(tokenlist, 0, tokenlist.size()-1);
	}
	
	/**
	 * Gets the ngram from the position specified by 's', to 
	 * the position (included) specified by 'e'
	 * @param tokenlist
	 * @param s
	 * @param e
	 * @return
	 */
	public static String ngram(List<String> tokenlist, int s, int e){
		StringBuilder buffer = new StringBuilder();
		for ( int i = s; i <= e; i++ ){
			buffer.append(tokenlist.get(i));
			if ( i != e )
				buffer.append(SEPARATOR_CHAR);
		}
		
		return buffer.toString();
	}
	
	public static String numListToStr(List<Integer> tokenlist){
		StringBuilder buffer = new StringBuilder();
		for ( int i = 0; i < tokenlist.size(); i++ ){
			buffer.append(String.valueOf(tokenlist.get(i)));
			if ( i != tokenlist.size()-1 )
				buffer.append(SEPARATOR_CHAR);
		}
		
		return buffer.toString();
	}
	public static <K,V> List<KeyValueObj<K,V>> topN(
			Map<V, K> map, final Comparator<K> cmp,
			int n){
		List<KeyValueObj<K,V>> sortedList = 
				sort(map, cmp);
		while ( sortedList.size() > n ){
			sortedList.remove(0);
		}
		
		return sortedList;
	}
	
	public static <K,V> List<KeyValueObj<K,V>> sort(
			Map<V, K> map,
			final Comparator<K> cmp){
		Comparator<KeyValueObj<K,V>> kvo_cmp = 
				new Comparator<KeyValueObj<K,V>>(){

					@Override
					public int compare(KeyValueObj<K,V> o1, KeyValueObj<K,V> o2) {
						// TODO Auto-generated method stub
						return cmp.compare(o1.getKey(), o2.getKey());
					}
		};
		
		List<KeyValueObj<K,V>> list = 
				new ArrayList<KeyValueObj<K,V>>();
		for ( V v : map.keySet()){
			K k = map.get(v);
			list.add(new KeyValueObj<K, V>(k,v));
		}
		Collections.sort(list, kvo_cmp);
		
		return list;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) throws IOException{
		// TODO Auto-generated method stub
        Date date = new Date();
        System.out.println("###Program starts at " + date);
        TweetSegmentationBySCP tweetSegmenter = 
            new TweetSegmentationBySCP();
        String datapath = "/home/yanxia/SED/ni_data/word/";
        boolean getGramTweetOne = false;
        boolean tweetOne = false;
        boolean getGramFromFile = false;
        boolean tweetFromFile = true;
// one tweet ngram 
		String tweet = " rttest __ RT@B RT @A RT@Jayjabz01 Wedding @jayjabz01 amp ab@SenoritaFaqaty gooooooood";
        tweet = tweet.replaceAll("[_]+", "_");
        if (getGramTweetOne == true){
            System.out.println(tweet);
            List<String> tokenlist = tweetSegmenter.tokenizeTweet(tweet);
            for (String token:tokenlist){
                System.out.print(token + "|");
            }
            for (int i = 0; i < tokenlist.size(); i++) {
                String ngram = ngram(tokenlist, 0, i);
                ngram = ngram.replaceAll("[_]+", "_");
                if (i < N) {
                    System.out.println(ngram);
                }
                if (i > 0) { // dynamic programming
                    for (int j = 0; j < i; j++) { 
                        if ( i - j > N )
                            continue;
                        ngram = ngram(tokenlist, j+1, i);
                        ngram = ngram.replaceAll("[_]+", "_");
                        System.out.println(ngram);
                    }
                }
            }
        }
// one tweet segment
        if (tweetOne == true){
            List<ScoredSegment> sslist = 
                tweetSegmenter.tweetSegmentBySCP(tweet);
            StringBuilder buffer = new StringBuilder();
            for ( int i = 0; i < sslist.size(); i++ ){
                ScoredSegment ss = sslist.get(i);
                List<String> seglist = ss.getSeg();
                String seg = ngram(seglist);
                buffer.append(seg).append(' ');
            }
            System.out.println(buffer.toString().trim());
        }
// read tweet from files, get tweet ngram segments
        if (getGramFromFile == true){
            File dir = new File(datapath);
            String subFileNames[] = dir.list();
            Arrays.sort(subFileNames);
            for (int id = 0; id < subFileNames.length; id ++){
                File subFile = new File(datapath + subFileNames[id]);
                if (subFile.isDirectory()){
                    continue;
                }
                if (! subFile.getName().startsWith("tweetCleanText")){
                    continue;
                }
                System.out.println("**********Reading file " + subFile.getAbsolutePath());
                String fileName = subFile.getName();
                String tStr = fileName.substring(fileName.length()-2, fileName.length());
                System.out.println("## Time window: " + tStr);
                File gramFile = new File(datapath + "ngrams_1505" + tStr);
                BufferedReader buffReader = new BufferedReader(new FileReader(subFile));
                BufferedWriter buffWriter = new BufferedWriter(new FileWriter(gramFile));
                HashMap<String, Integer> gramMap = new HashMap<String, Integer>();
                String lineStr = null;
                int lineNum = 0;
                while((lineStr = buffReader.readLine()) != null){
                    lineNum += 1;
//                    System.out.println(lineStr);
                    String tweetID = lineStr.substring(0, lineStr.indexOf("\t"));
                    String tweetContent = lineStr.substring(lineStr.indexOf("\t"));
                    List<String> tokenlist = tweetSegmenter.tokenizeTweet(tweetContent);
                    for (int i = 0; i < tokenlist.size(); i++) {
                        String ngram = ngram(tokenlist, 0, i);
                        ngram = ngram.replaceAll("[_]+", "_");
                        if (i < N) {
//                            System.out.println(ngram);
                            if (! gramMap.containsKey(ngram)){
                                gramMap.put(ngram, 1);
                            }
                        }
                        if (i > 0) { // dynamic programming
                            for (int j = 0; j < i; j++) { 
                                if ( i - j > N )
                                    continue;
                                ngram = ngram(tokenlist, j+1, i);
                                ngram = ngram.replaceAll("[_]+", "_");
//                                System.out.println(ngram);
                                if (! gramMap.containsKey(ngram)){
                                    gramMap.put(ngram, 1);
                                }
                            }
                        }
                    }
                    if (lineNum % 10000 == 0){
                        date = new Date();
                        System.out.println("###" + lineNum + " tweets are processed at " + date);
                    }
                }
                for (String gram : gramMap.keySet()) {
                    buffWriter.write(gram);
                    buffWriter.newLine();
                    buffWriter.flush();
                }
                date = new Date();
                System.out.println("###" + gramMap.size() + " grams are writen to " + gramFile.getName() + " at " + date);
                buffWriter.close();
                buffReader.close();
            }
        }
// read tweet from files, segment tweet
        if (tweetFromFile == true){
            tweetSegmenter.loadWikiGramMap();
            File dir = new File(datapath);
            String subFileNames[] = dir.list();
            Arrays.sort(subFileNames);
            for (int id = 0; id < subFileNames.length; id ++){
                File subFile = new File(datapath + subFileNames[id]);
                if (subFile.isDirectory()){
                    continue;
                }
                if (! subFile.getName().startsWith("tweetCleanText")){
                    continue;
                }
                System.out.println("**********Reading file " + subFile.getAbsolutePath());
                String fileName = subFile.getName();
                String tStr = fileName.substring(fileName.length()-2, fileName.length());
                System.out.println("## Time window: " + tStr);
                //String gramFilePath = datapath + "ngrams_prob_1505" + tStr;
                String gramFilePath = MS_GRAM_FILE;
                tweetSegmenter.loadMSNGramMap(gramFilePath);
                File seggedFile = new File(datapath + "segged_" + subFile.getName());
                BufferedReader buffReader = new BufferedReader(new FileReader(subFile));
                BufferedWriter buffWriter = new BufferedWriter(new FileWriter(seggedFile));
                String lineStr = null;
                int lineNum = 0;
                while((lineStr = buffReader.readLine()) != null){
                    lineNum += 1;
                    System.out.println(lineStr);
                    String tweetID = lineStr.substring(0, lineStr.indexOf("\t"));
                    String tweetContent = lineStr.substring(lineStr.indexOf("\t"));
                    List<ScoredSegment> sslist = 
                        tweetSegmenter.tweetSegmentBySCP(tweetContent);
                    if (sslist == null){
                        continue;
                    }
                    if (sslist.size() < 1){
                        continue;
                    }
//                    System.out.println("### tweet Content: " + tweetContent);
                    StringBuilder buffer = new StringBuilder();
                    double score = 0.0;
                    for ( int i = 0; i < sslist.size(); i++ ){
                        ScoredSegment ss = sslist.get(i);
                        List<String> seglist = ss.getSeg();
                        String seg = ngram(seglist);
                        seg = seg.replaceAll("[_]+", "_");
                        seg = seg.replaceAll("^_", "");
                        seg = seg.replaceAll("_$", "");
                        seg = seg.trim();
                        buffer.append(seg).append(' ');
                        score += ss.score();
                    }
                    String seggedStrOri = buffer.toString().trim();
                    String seggedStr = seggedStrOri.replaceAll(" ", "|");
                    seggedStr = seggedStr.replaceAll("_", " ");
//                    System.out.println("### segged Content: " + seggedStr);
                    buffWriter.write(tweetID + "\t" + score + "\t");
                    buffWriter.write(seggedStr);
                    buffWriter.newLine();
                    buffWriter.flush();
                    if (lineNum % 10000 == 0){
                        date = new Date();
                        System.out.println("###" + lineNum + " tweets are processed at " + date);
                    }
                }
                buffReader.close();
                buffWriter.close();
                date = new Date();
                System.out.println("### segged tweets are writen to " + seggedFile.getName() + " at " + date);
            }
        }
        date = new Date();
        System.out.println("###Program ends at " + date);
	}

}

class ScoredSegment {
	private List<String> seg;
	private double score;
	
	private Object data;
	
	public ScoredSegment(String[] ngrams, double score){
		seg = new ArrayList<String>();
		for ( int i = 0; i < ngrams.length; i++ ){
			seg.add(ngrams[i]);
		}
		this.score = score;
	}
	
	public ScoredSegment(List<String> seg, double score){
		this.seg = seg;
		this.score = score;
	}
	
	public void setData(Object data){
		this.data = data;
	}
	
	public Object getData(){
		return data;
	}
	
	public List<String> getSeg(){
		return seg;
	}
	
	void setScore(double score){
		this.score = score;
	}
	
	public double score(){
		return score;
	}
}

class KeyValueObj<K, V> {
	
	private K key;
	
	private V value;
	
	public KeyValueObj(K key, V value){
		this.key = key;
		this.value = value;
	}
	
	public K getKey(){
		return key;
	}
	
	public V getValue(){
		return value;
	}
	
	@Override
	public boolean equals(Object o){
		if ( o == this )
			return true;
		
		if ( o instanceof KeyValueObj ){
			KeyValueObj kvo = (KeyValueObj)o;
			if ( key.equals(kvo.key) && value.equals(kvo.value))
				return true;
		}
		
		return false;
	}
}
