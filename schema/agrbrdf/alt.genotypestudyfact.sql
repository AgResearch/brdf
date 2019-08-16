--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypestudyfact
    ADD CONSTRAINT "$1" FOREIGN KEY (genotypestudy) REFERENCES genotypestudy(obid);


