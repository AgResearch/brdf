--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplingfact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosamplingfunction) REFERENCES biosamplingfunction(obid);


