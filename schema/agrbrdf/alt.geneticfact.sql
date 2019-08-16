--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticfact
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


