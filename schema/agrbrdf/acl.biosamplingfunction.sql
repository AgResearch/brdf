--
-- Name: biosamplingfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplingfunction FROM PUBLIC;
REVOKE ALL ON TABLE biosamplingfunction FROM agrbrdf;
GRANT ALL ON TABLE biosamplingfunction TO agrbrdf;
GRANT SELECT ON TABLE biosamplingfunction TO gbs;


