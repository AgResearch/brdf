--
-- Name: phenotypeobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE phenotypeobservation FROM PUBLIC;
REVOKE ALL ON TABLE phenotypeobservation FROM agrbrdf;
GRANT ALL ON TABLE phenotypeobservation TO agrbrdf;
GRANT SELECT ON TABLE phenotypeobservation TO gbs;


