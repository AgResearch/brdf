--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: biosamplingfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT biosamplingfunction_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$4" FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$5" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $6; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfunction
    ADD CONSTRAINT "$6" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


