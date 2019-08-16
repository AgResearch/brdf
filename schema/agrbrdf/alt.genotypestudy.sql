--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: genotypestudy_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT genotypestudy_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$2" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$3" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$4" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$5" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: $6; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudy
    ADD CONSTRAINT "$6" FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


